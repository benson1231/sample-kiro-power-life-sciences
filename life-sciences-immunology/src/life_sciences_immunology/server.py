"""Immunology MCP server entry point.

Creates an ``ImmunologyServer`` that extends :class:`BaseLifeSciencesServer`
and registers all immunology tools.  The server is started via stdio
transport when run as ``uvx life-sciences-immunology``.
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
    abysis_client,
    iedb_client,
    imgt_client,
    immport_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # IEDB
    Tool(
        name="iedb_search",
        description="Search IEDB for immune epitopes by antigen.",
        inputSchema={
            "type": "object",
            "properties": {
                "antigen": {"type": "string", "description": "Antigen name or sequence."},
                "organism": {
                    "type": "string",
                    "description": "Source organism filter.",
                    "default": "",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["antigen"],
        },
    ),
    # ImmPort
    Tool(
        name="immport_search",
        description="Search ImmPort immunology studies. Requires IMMPORT_USERNAME and IMMPORT_PASSWORD.",
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
    # IMGT
    Tool(
        name="imgt_search",
        description="Search IMGT for immunoglobulin and T-cell receptor gene information.",
        inputSchema={
            "type": "object",
            "properties": {
                "gene": {"type": "string", "description": "Gene name (e.g. 'IGHV1-2')."},
                "species": {
                    "type": "string",
                    "description": "Species name.",
                    "default": "Homo sapiens",
                },
            },
            "required": ["gene"],
        },
    ),
    # abYsis
    Tool(
        name="abysis_analyze",
        description="Analyze an antibody sequence using abYsis.",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "Antibody amino acid sequence."},
            },
            "required": ["sequence"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "ImmunologyServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "iedb_search": lambda args: iedb_client.search(
            base, args["antigen"], args.get("organism", ""), args.get("max_results", 10),
        ),
        "immport_search": lambda args: immport_client.search(
            base, args["keyword"], args.get("max_results", 10),
        ),
        "imgt_search": lambda args: imgt_client.search(
            base, args["gene"], args.get("species", "Homo sapiens"),
        ),
        "abysis_analyze": lambda args: abysis_client.analyze(
            base, args["sequence"],
        ),
    }


# ---------------------------------------------------------------------------
# ImmunologyServer
# ---------------------------------------------------------------------------


class ImmunologyServer(BaseLifeSciencesServer):
    """MCP server for immunology databases.

    Databases covered: IEDB, ImmPort, IMGT, abYsis.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-immunology")
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
    """Start the immunology MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    immunology = ImmunologyServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await immunology.server.run(
                read_stream,
                write_stream,
                immunology.server.create_initialization_options(),
            )
    finally:
        await immunology.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-immunology``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
