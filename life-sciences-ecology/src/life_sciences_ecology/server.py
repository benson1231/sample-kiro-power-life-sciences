"""Ecology and Environmental Biology MCP server entry point.

Creates an ``EcologyServer`` that extends :class:`BaseLifeSciencesServer`
and registers all ecology tools.  The server is started via stdio
transport when run as ``uvx life-sciences-ecology``.
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
    bold_client,
    gbif_client,
    genbank_env_client,
    inaturalist_client,
    iucn_client,
    mgnify_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="gbif_occurrences",
        description="Search GBIF species occurrences by scientific name.",
        inputSchema={
            "type": "object",
            "properties": {
                "species": {"type": "string", "description": "Scientific species name."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["species"],
        },
    ),
    Tool(
        name="gbif_taxonomy",
        description="Search GBIF taxonomy by species name.",
        inputSchema={
            "type": "object",
            "properties": {
                "species": {"type": "string", "description": "Species name."},
            },
            "required": ["species"],
        },
    ),
    Tool(
        name="bold_search",
        description="Search BOLD barcode records by taxon name.",
        inputSchema={
            "type": "object",
            "properties": {
                "taxon": {"type": "string", "description": "Taxon name."},
            },
            "required": ["taxon"],
        },
    ),
    Tool(
        name="inaturalist_search",
        description="Search iNaturalist observations by taxon name.",
        inputSchema={
            "type": "object",
            "properties": {
                "taxon": {"type": "string", "description": "Taxon name."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["taxon"],
        },
    ),
    Tool(
        name="iucn_species",
        description="Get IUCN Red List status for a species. Requires IUCN_API_KEY.",
        inputSchema={
            "type": "object",
            "properties": {
                "species": {"type": "string", "description": "Species name."},
            },
            "required": ["species"],
        },
    ),
    Tool(
        name="genbank_env_search",
        description="Search GenBank environmental sequences by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword."},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="mgnify_search",
        description="Search MGnify metagenomics studies by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword."},
            },
            "required": ["keyword"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "EcologyServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "gbif_occurrences": lambda args: gbif_client.occurrences(
            base, args["species"], args.get("max_results", 10),
        ),
        "gbif_taxonomy": lambda args: gbif_client.taxonomy(
            base, args["species"],
        ),
        "bold_search": lambda args: bold_client.search(
            base, args["taxon"],
        ),
        "inaturalist_search": lambda args: inaturalist_client.search(
            base, args["taxon"], args.get("max_results", 10),
        ),
        "iucn_species": lambda args: iucn_client.species(
            base, args["species"],
        ),
        "genbank_env_search": lambda args: genbank_env_client.search(
            base, args["query"],
        ),
        "mgnify_search": lambda args: mgnify_client.search(
            base, args["keyword"],
        ),
    }


# ---------------------------------------------------------------------------
# EcologyServer
# ---------------------------------------------------------------------------


class EcologyServer(BaseLifeSciencesServer):
    """MCP server for ecology and environmental biology databases.

    Databases covered: GBIF, BOLD, iNaturalist, IUCN Red List,
    GenBank Environmental, MGnify.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-ecology")
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
    """Start the ecology MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    ecology = EcologyServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await ecology.server.run(
                read_stream,
                write_stream,
                ecology.server.create_initialization_options(),
            )
    finally:
        await ecology.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-ecology``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
