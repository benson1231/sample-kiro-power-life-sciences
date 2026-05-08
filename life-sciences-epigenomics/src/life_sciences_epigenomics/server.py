"""Epigenomics MCP server entry point.

Creates an ``EpigenomicsServer`` that extends :class:`BaseLifeSciencesServer`
and registers all epigenomics tools.  The server is started via stdio
transport when run as ``uvx life-sciences-epigenomics``.
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
    ihec_client,
    methbase_client,
    roadmap_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="ihec_search",
        description="Search IHEC datasets by tissue type.",
        inputSchema={
            "type": "object",
            "properties": {
                "tissue": {"type": "string", "description": "Tissue type to search for."},
            },
            "required": ["tissue"],
        },
    ),
    Tool(
        name="roadmap_search",
        description="Search Roadmap Epigenomics data by tissue and optional histone mark.",
        inputSchema={
            "type": "object",
            "properties": {
                "tissue": {"type": "string", "description": "Tissue type to search for."},
                "mark": {
                    "type": "string",
                    "description": "Histone mark (e.g. 'H3K4me3').",
                    "default": "",
                },
            },
            "required": ["tissue"],
        },
    ),
    Tool(
        name="methbase_search",
        description="Search MethBase methylomes by species and optional tissue.",
        inputSchema={
            "type": "object",
            "properties": {
                "species": {"type": "string", "description": "Species name."},
                "tissue": {
                    "type": "string",
                    "description": "Tissue type.",
                    "default": "",
                },
            },
            "required": ["species"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "EpigenomicsServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "ihec_search": lambda args: ihec_client.search(
            base, args["tissue"],
        ),
        "roadmap_search": lambda args: roadmap_client.search(
            base, args["tissue"], args.get("mark", ""),
        ),
        "methbase_search": lambda args: methbase_client.search(
            base, args["species"], args.get("tissue", ""),
        ),
    }


# ---------------------------------------------------------------------------
# EpigenomicsServer
# ---------------------------------------------------------------------------


class EpigenomicsServer(BaseLifeSciencesServer):
    """MCP server for epigenomics databases.

    Databases covered: IHEC, Roadmap Epigenomics, MethBase.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-epigenomics")
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
    """Start the epigenomics MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    epigenomics = EpigenomicsServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await epigenomics.server.run(
                read_stream,
                write_stream,
                epigenomics.server.create_initialization_options(),
            )
    finally:
        await epigenomics.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-epigenomics``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
