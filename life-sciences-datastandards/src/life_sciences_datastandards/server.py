"""Data Standards and Formats MCP server entry point.

Creates a ``DataStandardsServer`` that extends :class:`BaseLifeSciencesServer`
and registers all data standards tools.  The server is started via stdio
transport when run as ``uvx life-sciences-datastandards``.
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
    biopax_client,
    isatab_client,
    magetab_client,
    sbml_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="magetab_validate",
        description="Validate MAGE-TAB formatted content.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "MAGE-TAB content to validate."},
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="magetab_parse",
        description="Parse MAGE-TAB formatted content into structured data.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "MAGE-TAB content to parse."},
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="isatab_validate",
        description="Validate ISA-Tab formatted content.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "ISA-Tab content to validate."},
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="isatab_parse",
        description="Parse ISA-Tab formatted content into structured data.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "ISA-Tab content to parse."},
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="sbml_validate",
        description="Validate SBML formatted content.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "SBML content to validate."},
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="sbml_parse",
        description="Parse SBML formatted content into structured data.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "SBML content to parse."},
            },
            "required": ["content"],
        },
    ),
    Tool(
        name="biopax_parse",
        description="Parse BioPAX formatted content into structured data.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "BioPAX content to parse."},
            },
            "required": ["content"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "DataStandardsServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "magetab_validate": lambda args: magetab_client.validate(
            base, args["content"],
        ),
        "magetab_parse": lambda args: magetab_client.parse(
            base, args["content"],
        ),
        "isatab_validate": lambda args: isatab_client.validate(
            base, args["content"],
        ),
        "isatab_parse": lambda args: isatab_client.parse(
            base, args["content"],
        ),
        "sbml_validate": lambda args: sbml_client.validate(
            base, args["content"],
        ),
        "sbml_parse": lambda args: sbml_client.parse(
            base, args["content"],
        ),
        "biopax_parse": lambda args: biopax_client.parse(
            base, args["content"],
        ),
    }


# ---------------------------------------------------------------------------
# DataStandardsServer
# ---------------------------------------------------------------------------


class DataStandardsServer(BaseLifeSciencesServer):
    """MCP server for data standards and formats.

    Tools covered: MAGE-TAB, ISA-Tab, SBML, BioPAX.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-datastandards")
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
    """Start the data standards MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    datastandards = DataStandardsServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await datastandards.server.run(
                read_stream,
                write_stream,
                datastandards.server.create_initialization_options(),
            )
    finally:
        await datastandards.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-datastandards``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
