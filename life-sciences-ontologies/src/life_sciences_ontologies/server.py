"""Ontologies MCP server entry point.

Creates an ``OntologiesServer`` that extends :class:`BaseLifeSciencesServer`
and registers all ontology tools.  The server is started via stdio
transport when run as ``uvx life-sciences-ontologies``.
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
    disease_ontology_client,
    go_client,
    hpo_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # Gene Ontology
    Tool(
        name="go_search",
        description="Search Gene Ontology terms by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "term": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'apoptosis', 'kinase activity').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["term"],
        },
    ),
    Tool(
        name="go_term",
        description="Get GO term details by GO ID (e.g. 'GO:0008150').",
        inputSchema={
            "type": "object",
            "properties": {
                "go_id": {
                    "type": "string",
                    "description": "Gene Ontology identifier (e.g. 'GO:0008150').",
                },
            },
            "required": ["go_id"],
        },
    ),
    Tool(
        name="go_annotations",
        description="Get gene annotations for a GO term.",
        inputSchema={
            "type": "object",
            "properties": {
                "go_id": {
                    "type": "string",
                    "description": "Gene Ontology identifier (e.g. 'GO:0008150').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 20,
                },
            },
            "required": ["go_id"],
        },
    ),
    # HPO
    Tool(
        name="hpo_search",
        description="Search HPO phenotype terms by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "term": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'seizure', 'intellectual disability').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["term"],
        },
    ),
    Tool(
        name="hpo_term",
        description="Get HPO term details by HPO ID (e.g. 'HP:0001250').",
        inputSchema={
            "type": "object",
            "properties": {
                "hpo_id": {
                    "type": "string",
                    "description": "HPO identifier (e.g. 'HP:0001250').",
                },
            },
            "required": ["hpo_id"],
        },
    ),
    # Disease Ontology
    Tool(
        name="disease_ontology_search",
        description="Search Disease Ontology by term.",
        inputSchema={
            "type": "object",
            "properties": {
                "term": {
                    "type": "string",
                    "description": "Disease Ontology term or DOID (e.g. '0050686').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["term"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "OntologiesServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "go_search": lambda args: go_client.search(
            base, args["term"], args.get("max_results", 10),
        ),
        "go_term": lambda args: go_client.get_term(
            base, args["go_id"],
        ),
        "go_annotations": lambda args: go_client.annotations(
            base, args["go_id"], args.get("max_results", 20),
        ),
        "hpo_search": lambda args: hpo_client.search(
            base, args["term"], args.get("max_results", 10),
        ),
        "hpo_term": lambda args: hpo_client.get_term(
            base, args["hpo_id"],
        ),
        "disease_ontology_search": lambda args: disease_ontology_client.search(
            base, args["term"], args.get("max_results", 10),
        ),
    }


# ---------------------------------------------------------------------------
# OntologiesServer
# ---------------------------------------------------------------------------


class OntologiesServer(BaseLifeSciencesServer):
    """MCP server for ontology databases.

    Databases covered: Gene Ontology, HPO, Disease Ontology.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-ontologies")
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
    """Start the ontologies MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    ontologies = OntologiesServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await ontologies.server.run(
                read_stream,
                write_stream,
                ontologies.server.create_initialization_options(),
            )
    finally:
        await ontologies.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-ontologies``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
