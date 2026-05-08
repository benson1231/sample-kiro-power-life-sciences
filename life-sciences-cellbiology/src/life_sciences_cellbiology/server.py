"""Cell Biology MCP server entry point.

Creates a ``CellBiologyServer`` that extends :class:`BaseLifeSciencesServer`
and registers all cell biology tools.  The server is started via stdio
transport when run as ``uvx life-sciences-cellbiology``.
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
    cell_atlas_client,
    cellxgene_client,
    scea_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="cell_atlas_search",
        description="Search Human Cell Atlas by gene symbol.",
        inputSchema={
            "type": "object",
            "properties": {
                "gene": {"type": "string", "description": "Gene symbol."},
            },
            "required": ["gene"],
        },
    ),
    Tool(
        name="cellxgene_datasets",
        description="List CellxGene datasets, optionally filtered by tissue and/or cell type.",
        inputSchema={
            "type": "object",
            "properties": {
                "tissue": {
                    "type": "string",
                    "description": "Tissue type filter.",
                    "default": "",
                },
                "cell_type": {
                    "type": "string",
                    "description": "Cell type filter.",
                    "default": "",
                },
            },
        },
    ),
    Tool(
        name="cellxgene_expression",
        description="Get gene expression data from a CellxGene dataset.",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string", "description": "CellxGene dataset ID."},
                "gene": {"type": "string", "description": "Gene symbol."},
            },
            "required": ["dataset_id", "gene"],
        },
    ),
    Tool(
        name="scea_search",
        description="Search Single Cell Expression Atlas by gene and optional species.",
        inputSchema={
            "type": "object",
            "properties": {
                "gene": {"type": "string", "description": "Gene symbol."},
                "species": {
                    "type": "string",
                    "description": "Species name.",
                    "default": "",
                },
            },
            "required": ["gene"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "CellBiologyServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "cell_atlas_search": lambda args: cell_atlas_client.search(
            base, args["gene"],
        ),
        "cellxgene_datasets": lambda args: cellxgene_client.datasets(
            base, args.get("tissue", ""), args.get("cell_type", ""),
        ),
        "cellxgene_expression": lambda args: cellxgene_client.expression(
            base, args["dataset_id"], args["gene"],
        ),
        "scea_search": lambda args: scea_client.search(
            base, args["gene"], args.get("species", ""),
        ),
    }


# ---------------------------------------------------------------------------
# CellBiologyServer
# ---------------------------------------------------------------------------


class CellBiologyServer(BaseLifeSciencesServer):
    """MCP server for cell biology databases.

    Databases covered: Cell Atlas, CellxGene, Single Cell Expression Atlas.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-cellbiology")
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
    """Start the cell biology MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    cellbiology = CellBiologyServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await cellbiology.server.run(
                read_stream,
                write_stream,
                cellbiology.server.create_initialization_options(),
            )
    finally:
        await cellbiology.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-cellbiology``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
