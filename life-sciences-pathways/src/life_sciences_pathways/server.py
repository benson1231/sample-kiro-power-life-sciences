"""Pathways and Interactions MCP server entry point.

Creates a ``PathwaysServer`` that extends :class:`BaseLifeSciencesServer`
and registers all pathway and interaction tools.  The server is started via
stdio transport when run as ``uvx life-sciences-pathways``.
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
    biocyc_client,
    intact_client,
    kegg_client,
    reactome_client,
    wikipathways_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # KEGG
    Tool(
        name="kegg_pathway",
        description="Get KEGG pathway by pathway ID (e.g. 'hsa04110').",
        inputSchema={
            "type": "object",
            "properties": {
                "pathway_id": {
                    "type": "string",
                    "description": "KEGG pathway identifier (e.g. 'hsa04110').",
                },
            },
            "required": ["pathway_id"],
        },
    ),
    Tool(
        name="kegg_search",
        description="Search KEGG pathways by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'apoptosis').",
                },
            },
            "required": ["query"],
        },
    ),
    # Reactome
    Tool(
        name="reactome_search",
        description="Search Reactome pathways by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'cell cycle').",
                },
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
        name="reactome_pathway",
        description="Get Reactome pathway details by stable ID (e.g. 'R-HSA-1640170').",
        inputSchema={
            "type": "object",
            "properties": {
                "stable_id": {
                    "type": "string",
                    "description": "Reactome stable identifier (e.g. 'R-HSA-1640170').",
                },
            },
            "required": ["stable_id"],
        },
    ),
    # BioCyc
    Tool(
        name="biocyc_pathway",
        description="Get BioCyc pathway by pathway ID and organism.",
        inputSchema={
            "type": "object",
            "properties": {
                "pathway_id": {
                    "type": "string",
                    "description": "BioCyc pathway identifier.",
                },
                "organism": {
                    "type": "string",
                    "description": "Organism database code (e.g. 'HUMAN', 'ECOLI').",
                    "default": "HUMAN",
                },
            },
            "required": ["pathway_id"],
        },
    ),
    # WikiPathways
    Tool(
        name="wikipathways_search",
        description="Search WikiPathways by text query.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string.",
                },
                "organism": {
                    "type": "string",
                    "description": "Species name (e.g. 'Homo sapiens').",
                    "default": "Homo sapiens",
                },
            },
            "required": ["query"],
        },
    ),
    # IntAct
    Tool(
        name="intact_interactions",
        description="Get molecular interactions for a protein from IntAct.",
        inputSchema={
            "type": "object",
            "properties": {
                "protein": {
                    "type": "string",
                    "description": "Protein name or accession (e.g. 'TP53', 'P04637').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["protein"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "PathwaysServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "kegg_pathway": lambda args: kegg_client.pathway(
            base, args["pathway_id"],
        ),
        "kegg_search": lambda args: kegg_client.search(
            base, args["query"],
        ),
        "reactome_search": lambda args: reactome_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "reactome_pathway": lambda args: reactome_client.pathway(
            base, args["stable_id"],
        ),
        "biocyc_pathway": lambda args: biocyc_client.pathway(
            base, args["pathway_id"], args.get("organism", "HUMAN"),
        ),
        "wikipathways_search": lambda args: wikipathways_client.search(
            base, args["query"], args.get("organism", "Homo sapiens"),
        ),
        "intact_interactions": lambda args: intact_client.interactions(
            base, args["protein"], args.get("max_results", 10),
        ),
    }


# ---------------------------------------------------------------------------
# PathwaysServer
# ---------------------------------------------------------------------------


class PathwaysServer(BaseLifeSciencesServer):
    """MCP server for pathway and interaction databases.

    Databases covered: KEGG, Reactome, BioCyc, WikiPathways, IntAct.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-pathways")
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
    """Start the pathways MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    pathways = PathwaysServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await pathways.server.run(
                read_stream,
                write_stream,
                pathways.server.create_initialization_options(),
            )
    finally:
        await pathways.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-pathways``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
