"""AI/ML for Life Sciences MCP server entry point.

Creates an ``AIMLServer`` that extends :class:`BaseLifeSciencesServer`
and registers all AI/ML tools.  The server is started via stdio
transport when run as ``uvx life-sciences-aiml``.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from life_sciences_common import BaseLifeSciencesServer

from .clients import (
    alphafold_client,
    bionlp_client,
    esm_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="esm_embeddings",
        description="Get ESM protein embeddings for a sequence.",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "Protein amino acid sequence."},
            },
            "required": ["sequence"],
        },
    ),
    Tool(
        name="esm_structure",
        description="Predict protein structure using ESMFold.",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "Protein amino acid sequence."},
            },
            "required": ["sequence"],
        },
    ),
    Tool(
        name="alphafold_predict",
        description="Submit a protein sequence for AlphaFold structure prediction.",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "Protein amino acid sequence."},
            },
            "required": ["sequence"],
        },
    ),
    Tool(
        name="alphafold_status",
        description="Get the status of an AlphaFold prediction job.",
        inputSchema={
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "AlphaFold job ID."},
            },
            "required": ["job_id"],
        },
    ),
    Tool(
        name="bionlp_entities",
        description="Extract biomedical entities from text using BioNLP.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Biomedical text to analyze."},
            },
            "required": ["text"],
        },
    ),
    Tool(
        name="bionlp_qa",
        description="Answer a biomedical question given context using BioNLP.",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Biomedical question."},
                "context": {"type": "string", "description": "Context text for the question."},
            },
            "required": ["question", "context"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "AIMLServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "esm_embeddings": lambda args: esm_client.embeddings(
            base, args["sequence"],
        ),
        "esm_structure": lambda args: esm_client.structure(
            base, args["sequence"],
        ),
        "alphafold_predict": lambda args: alphafold_client.predict(
            base, args["sequence"],
        ),
        "alphafold_status": lambda args: alphafold_client.status(
            base, args["job_id"],
        ),
        "bionlp_entities": lambda args: bionlp_client.entities(
            base, args["text"],
        ),
        "bionlp_qa": lambda args: bionlp_client.qa(
            base, args["question"], args["context"],
        ),
    }


# ---------------------------------------------------------------------------
# AIMLServer
# ---------------------------------------------------------------------------


class AIMLServer(BaseLifeSciencesServer):
    """MCP server for AI/ML tools in life sciences.

    Tools covered: ESM embeddings, ESMFold structure prediction,
    AlphaFold prediction, BioNLP entity extraction and QA.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-aiml")
        self._dispatch = _build_dispatch(self)
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register list_tools and call_tool handlers on the MCP server."""

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return TOOLS

        dispatch = self._dispatch

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None = None,
        ) -> list[TextContent]:
            if name not in dispatch:
                raise ValueError(f"Unknown tool: {name}")
            result = await dispatch[name](arguments or {})
            return [TextContent(type="text", text=json.dumps(result, default=str))]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def _run() -> None:
    """Start the AI/ML MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    aiml = AIMLServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await aiml.server.run(
                read_stream,
                write_stream,
                aiml.server.create_initialization_options(),
            )
    finally:
        await aiml.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-aiml``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
