"""Microbiology and Metagenomics MCP server entry point.

Creates a ``MicrobiologyServer`` that extends :class:`BaseLifeSciencesServer`
and registers all microbiology tools.  The server is started via stdio
transport when run as ``uvx life-sciences-microbiology``.
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
    bvbrc_client,
    card_client,
    greengenes_client,
    mgrast_client,
    qiime2_client,
    silva_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # SILVA
    Tool(
        name="silva_search",
        description="Search SILVA rRNA database for ribosomal RNA sequences.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (e.g. organism name or accession)."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    # Greengenes
    Tool(
        name="greengenes_search",
        description="Search Greengenes 16S rRNA taxonomy database.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Taxonomy or organism query."},
            },
            "required": ["query"],
        },
    ),
    # QIIME 2
    Tool(
        name="qiime2_action",
        description="Run a QIIME 2 microbiome analysis action.",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "QIIME 2 action (e.g. 'import', 'dada2', 'classify', 'diversity').",
                },
                "inputs": {
                    "type": "object",
                    "description": "Action-specific input parameters.",
                },
            },
            "required": ["action", "inputs"],
        },
    ),
    # MG-RAST
    Tool(
        name="mgrast_search",
        description="Search MG-RAST metagenomics database.",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["keyword"],
        },
    ),
    # BV-BRC
    Tool(
        name="bvbrc_search",
        description="Search BV-BRC for bacterial and viral genomes.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (e.g. organism name)."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="bvbrc_features",
        description="Get genomic features for a BV-BRC genome.",
        inputSchema={
            "type": "object",
            "properties": {
                "genome_id": {"type": "string", "description": "BV-BRC genome identifier."},
            },
            "required": ["genome_id"],
        },
    ),
    # CARD
    Tool(
        name="card_search",
        description="Search CARD for antibiotic resistance genes.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (e.g. gene name or antibiotic)."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="card_analyze",
        description="Analyze a DNA sequence for antibiotic resistance genes using CARD.",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "DNA sequence to analyze."},
            },
            "required": ["sequence"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "MicrobiologyServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "silva_search": lambda args: silva_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "greengenes_search": lambda args: greengenes_client.search(
            base, args["query"],
        ),
        "qiime2_action": lambda args: qiime2_client.action(
            base, args["action"], args.get("inputs", {}),
        ),
        "mgrast_search": lambda args: mgrast_client.search(
            base, args["keyword"], args.get("max_results", 10),
        ),
        "bvbrc_search": lambda args: bvbrc_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "bvbrc_features": lambda args: bvbrc_client.features(
            base, args["genome_id"],
        ),
        "card_search": lambda args: card_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "card_analyze": lambda args: card_client.analyze(
            base, args["sequence"],
        ),
    }


# ---------------------------------------------------------------------------
# MicrobiologyServer
# ---------------------------------------------------------------------------


class MicrobiologyServer(BaseLifeSciencesServer):
    """MCP server for microbiology and metagenomics databases.

    Databases covered: SILVA, Greengenes, QIIME 2, MG-RAST, BV-BRC, CARD.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-microbiology")
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
    """Start the microbiology MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    microbiology = MicrobiologyServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await microbiology.server.run(
                read_stream,
                write_stream,
                microbiology.server.create_initialization_options(),
            )
    finally:
        await microbiology.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-microbiology``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
