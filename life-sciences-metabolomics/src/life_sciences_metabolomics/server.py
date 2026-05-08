"""Metabolomics MCP server entry point.

Creates a ``MetabolomicsServer`` that extends :class:`BaseLifeSciencesServer`
and registers all metabolomics tools.  The server is started via stdio
transport when run as ``uvx life-sciences-metabolomics``.
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
    hmdb_client,
    massbank_client,
    metabolights_client,
    metlin_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # HMDB
    Tool(
        name="hmdb_search",
        description="Search HMDB for human metabolites by name or identifier.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Metabolite name or HMDB ID."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    # MetaboLights
    Tool(
        name="metabolights_search",
        description="Search MetaboLights metabolomics studies.",
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
    # METLIN
    Tool(
        name="metlin_search",
        description="Search METLIN metabolite database by exact mass.",
        inputSchema={
            "type": "object",
            "properties": {
                "mass": {
                    "type": "number",
                    "description": "Exact mass to search for.",
                },
                "tolerance": {
                    "type": "number",
                    "description": "Mass tolerance in Da.",
                    "default": 0.01,
                },
            },
            "required": ["mass"],
        },
    ),
    # MassBank
    Tool(
        name="massbank_search",
        description="Search MassBank mass spectra database.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Compound name, formula, or InChIKey."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "MetabolomicsServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "hmdb_search": lambda args: hmdb_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "metabolights_search": lambda args: metabolights_client.search(
            base, args["keyword"], args.get("max_results", 10),
        ),
        "metlin_search": lambda args: metlin_client.search(
            base, args["mass"], args.get("tolerance", 0.01),
        ),
        "massbank_search": lambda args: massbank_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
    }


# ---------------------------------------------------------------------------
# MetabolomicsServer
# ---------------------------------------------------------------------------


class MetabolomicsServer(BaseLifeSciencesServer):
    """MCP server for metabolomics databases.

    Databases covered: HMDB, MetaboLights, METLIN, MassBank.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-metabolomics")
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
    """Start the metabolomics MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    metabolomics = MetabolomicsServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await metabolomics.server.run(
                read_stream,
                write_stream,
                metabolomics.server.create_initialization_options(),
            )
    finally:
        await metabolomics.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-metabolomics``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
