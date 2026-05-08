"""Agricultural and Plant Biology MCP server entry point.

Creates an ``AgricultureServer`` that extends :class:`BaseLifeSciencesServer`
and registers all agriculture tools.  The server is started via stdio
transport when run as ``uvx life-sciences-agriculture``.
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
    gramene_client,
    phytozome_client,
    plantgdb_client,
    tair_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="phytozome_search",
        description="Search Phytozome plant genomes by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="tair_search",
        description="Search TAIR Arabidopsis data by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="gramene_search",
        description="Search Gramene comparative genomics data by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="plantgdb_search",
        description="Search PlantGDB plant genome data by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "AgricultureServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "phytozome_search": lambda args: phytozome_client.search(
            base, args["query"],
        ),
        "tair_search": lambda args: tair_client.search(
            base, args["query"],
        ),
        "gramene_search": lambda args: gramene_client.search(
            base, args["query"],
        ),
        "plantgdb_search": lambda args: plantgdb_client.search(
            base, args["query"],
        ),
    }


# ---------------------------------------------------------------------------
# AgricultureServer
# ---------------------------------------------------------------------------


class AgricultureServer(BaseLifeSciencesServer):
    """MCP server for agricultural and plant biology databases.

    Databases covered: Phytozome, TAIR, Gramene, PlantGDB.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-agriculture")
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
    """Start the agriculture MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    agriculture = AgricultureServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await agriculture.server.run(
                read_stream,
                write_stream,
                agriculture.server.create_initialization_options(),
            )
    finally:
        await agriculture.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-agriculture``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
