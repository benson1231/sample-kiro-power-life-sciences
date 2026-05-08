"""Neuroscience MCP server entry point.

Creates a ``NeuroscienceServer`` that extends :class:`BaseLifeSciencesServer`
and registers all neuroscience tools.  The server is started via stdio
transport when run as ``uvx life-sciences-neuroscience``.
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
    allen_brain_client,
    brainmap_client,
    neuromorpho_client,
    openneuro_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="allen_brain_search",
        description="Search Allen Brain Atlas gene expression data by gene symbol.",
        inputSchema={
            "type": "object",
            "properties": {
                "gene": {"type": "string", "description": "Gene symbol."},
            },
            "required": ["gene"],
        },
    ),
    Tool(
        name="allen_brain_structure",
        description="Get Allen Brain Atlas structure information by ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "structure_id": {"type": "string", "description": "Structure ID."},
            },
            "required": ["structure_id"],
        },
    ),
    Tool(
        name="neuromorpho_search",
        description="Search NeuroMorpho neuron morphologies by cell type and optional brain region.",
        inputSchema={
            "type": "object",
            "properties": {
                "cell_type": {"type": "string", "description": "Cell type."},
                "brain_region": {
                    "type": "string",
                    "description": "Brain region.",
                    "default": "",
                },
            },
            "required": ["cell_type"],
        },
    ),
    Tool(
        name="openneuro_search",
        description="Search OpenNeuro neuroimaging datasets by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword."},
            },
            "required": ["keyword"],
        },
    ),
    Tool(
        name="brainmap_search",
        description="Search BrainMap functional neuroimaging data by brain region.",
        inputSchema={
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Brain region."},
            },
            "required": ["region"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "NeuroscienceServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "allen_brain_search": lambda args: allen_brain_client.search(
            base, args["gene"],
        ),
        "allen_brain_structure": lambda args: allen_brain_client.structure(
            base, args["structure_id"],
        ),
        "neuromorpho_search": lambda args: neuromorpho_client.search(
            base, args["cell_type"], args.get("brain_region", ""),
        ),
        "openneuro_search": lambda args: openneuro_client.search(
            base, args["keyword"],
        ),
        "brainmap_search": lambda args: brainmap_client.search(
            base, args["region"],
        ),
    }


# ---------------------------------------------------------------------------
# NeuroscienceServer
# ---------------------------------------------------------------------------


class NeuroscienceServer(BaseLifeSciencesServer):
    """MCP server for neuroscience databases.

    Databases covered: Allen Brain Atlas, NeuroMorpho, OpenNeuro, BrainMap.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-neuroscience")
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
    """Start the neuroscience MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    neuroscience = NeuroscienceServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await neuroscience.server.run(
                read_stream,
                write_stream,
                neuroscience.server.create_initialization_options(),
            )
    finally:
        await neuroscience.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-neuroscience``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
