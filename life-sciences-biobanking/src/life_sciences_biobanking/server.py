"""Biobanking and Sample Management MCP server entry point.

Creates a ``BiobankingServer`` that extends :class:`BaseLifeSciencesServer`
and registers all biobanking tools.  The server is started via stdio
transport when run as ``uvx life-sciences-biobanking``.
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
    bbmri_client,
    biosample_client,
    inventory_client,
    lims_client,
    protocols_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="bbmri_search",
        description="Search BBMRI biobank collections by disease, material type, and/or country.",
        inputSchema={
            "type": "object",
            "properties": {
                "disease": {"type": "string", "description": "Disease filter.", "default": ""},
                "material": {"type": "string", "description": "Material type filter.", "default": ""},
                "country": {"type": "string", "description": "Country filter.", "default": ""},
            },
        },
    ),
    Tool(
        name="biosample_search",
        description="Search NCBI BioSample database by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword."},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="lims_sample",
        description="Get sample information by ID from LIMS.",
        inputSchema={
            "type": "object",
            "properties": {
                "sample_id": {"type": "string", "description": "Sample ID."},
            },
            "required": ["sample_id"],
        },
    ),
    Tool(
        name="lims_create_sample",
        description="Create a new sample in LIMS.",
        inputSchema={
            "type": "object",
            "properties": {
                "sample_type": {"type": "string", "description": "Sample type."},
                "metadata": {
                    "type": "object",
                    "description": "Sample metadata.",
                },
            },
            "required": ["sample_type", "metadata"],
        },
    ),
    Tool(
        name="inventory_search",
        description="Search sample inventory by type and/or location.",
        inputSchema={
            "type": "object",
            "properties": {
                "sample_type": {"type": "string", "description": "Sample type filter.", "default": ""},
                "location": {"type": "string", "description": "Location filter.", "default": ""},
            },
        },
    ),
    Tool(
        name="protocols_search",
        description="Search protocols.io for laboratory protocols by keyword.",
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


def _build_dispatch(base: "BiobankingServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "bbmri_search": lambda args: bbmri_client.search(
            base, args.get("disease", ""), args.get("material", ""), args.get("country", ""),
        ),
        "biosample_search": lambda args: biosample_client.search(
            base, args["query"],
        ),
        "lims_sample": lambda args: lims_client.get_sample(
            base, args["sample_id"],
        ),
        "lims_create_sample": lambda args: lims_client.create_sample(
            base, args["sample_type"], args["metadata"],
        ),
        "inventory_search": lambda args: inventory_client.search(
            base, args.get("sample_type", ""), args.get("location", ""),
        ),
        "protocols_search": lambda args: protocols_client.search(
            base, args["keyword"],
        ),
    }


# ---------------------------------------------------------------------------
# BiobankingServer
# ---------------------------------------------------------------------------


class BiobankingServer(BaseLifeSciencesServer):
    """MCP server for biobanking and sample management.

    Tools covered: BBMRI, BioSample, LIMS, Sample Inventory, protocols.io.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-biobanking")
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
    """Start the biobanking MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    biobanking = BiobankingServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await biobanking.server.run(
                read_stream,
                write_stream,
                biobanking.server.create_initialization_options(),
            )
    finally:
        await biobanking.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-biobanking``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
