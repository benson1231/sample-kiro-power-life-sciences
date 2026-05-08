"""Model Organisms MCP server entry point.

Creates a ``ModelOrganismsServer`` that extends :class:`BaseLifeSciencesServer`
and registers all model organism tools.  The server is started via stdio
transport when run as ``uvx life-sciences-model-organisms``.
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
    flybase_client,
    mgi_client,
    sgd_client,
    wormbase_client,
    zfin_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # FlyBase
    Tool(
        name="flybase_gene",
        description="Lookup a gene by symbol in FlyBase (Drosophila).",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Gene symbol (e.g. 'dpp', 'Notch').",
                },
            },
            "required": ["symbol"],
        },
    ),
    # WormBase
    Tool(
        name="wormbase_gene",
        description="Lookup a gene by name in WormBase (C. elegans).",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Gene name (e.g. 'unc-86', 'lin-12').",
                },
            },
            "required": ["name"],
        },
    ),
    # ZFIN
    Tool(
        name="zfin_gene",
        description="Lookup a gene by name in ZFIN (zebrafish).",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Gene name (e.g. 'shha', 'tp53').",
                },
            },
            "required": ["name"],
        },
    ),
    # MGI
    Tool(
        name="mgi_gene",
        description="Lookup a gene by symbol in MGI (mouse).",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Gene symbol (e.g. 'Trp53', 'Brca1').",
                },
            },
            "required": ["symbol"],
        },
    ),
    # SGD
    Tool(
        name="sgd_gene",
        description="Lookup a gene by name in SGD (yeast).",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Gene name (e.g. 'CDC28', 'RAD51').",
                },
            },
            "required": ["name"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "ModelOrganismsServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "flybase_gene": lambda args: flybase_client.gene(
            base, args["symbol"],
        ),
        "wormbase_gene": lambda args: wormbase_client.gene(
            base, args["name"],
        ),
        "zfin_gene": lambda args: zfin_client.gene(
            base, args["name"],
        ),
        "mgi_gene": lambda args: mgi_client.gene(
            base, args["symbol"],
        ),
        "sgd_gene": lambda args: sgd_client.gene(
            base, args["name"],
        ),
    }


# ---------------------------------------------------------------------------
# ModelOrganismsServer
# ---------------------------------------------------------------------------


class ModelOrganismsServer(BaseLifeSciencesServer):
    """MCP server for model organism databases.

    Databases covered: FlyBase, WormBase, ZFIN, MGI, SGD.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-model-organisms")
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
    """Start the model organisms MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    model_organisms = ModelOrganismsServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await model_organisms.server.run(
                read_stream,
                write_stream,
                model_organisms.server.create_initialization_options(),
            )
    finally:
        await model_organisms.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-model-organisms``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
