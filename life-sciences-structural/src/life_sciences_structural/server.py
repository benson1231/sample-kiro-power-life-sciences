"""Structural Biology MCP server entry point.

Creates a ``StructuralServer`` that extends :class:`BaseLifeSciencesServer`
and registers all structural biology tools.  The server is started via stdio
transport when run as ``uvx life-sciences-structural``.
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
    alphafold_client,
    cath_client,
    pdb_client,
    scop_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # PDB
    Tool(
        name="pdb_search",
        description="Search PDB structures by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string (e.g. 'hemoglobin', 'kinase').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="pdb_fetch",
        description="Fetch structure metadata by PDB ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "pdb_id": {
                    "type": "string",
                    "description": "PDB identifier (e.g. '1HHO', '4HHB').",
                },
            },
            "required": ["pdb_id"],
        },
    ),
    Tool(
        name="pdb_download",
        description="Download a structure file in PDB or mmCIF format.",
        inputSchema={
            "type": "object",
            "properties": {
                "pdb_id": {
                    "type": "string",
                    "description": "PDB identifier (e.g. '1HHO').",
                },
                "format": {
                    "type": "string",
                    "description": "File format ('pdb' or 'cif').",
                    "default": "pdb",
                },
            },
            "required": ["pdb_id"],
        },
    ),
    # AlphaFold DB
    Tool(
        name="alphafold_lookup",
        description="Get predicted structure from AlphaFold DB by UniProt accession.",
        inputSchema={
            "type": "object",
            "properties": {
                "uniprot_accession": {
                    "type": "string",
                    "description": "UniProt accession (e.g. 'P04637').",
                },
            },
            "required": ["uniprot_accession"],
        },
    ),
    # CATH
    Tool(
        name="cath_classify",
        description="Get CATH domain classification by domain ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain_id": {
                    "type": "string",
                    "description": "CATH domain identifier (e.g. '1cukA01').",
                },
            },
            "required": ["domain_id"],
        },
    ),
    # SCOP
    Tool(
        name="scop_classify",
        description="Get SCOP structural classification by PDB ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "pdb_id": {
                    "type": "string",
                    "description": "PDB identifier (e.g. '1HHO').",
                },
            },
            "required": ["pdb_id"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "StructuralServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "pdb_search": lambda args: pdb_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "pdb_fetch": lambda args: pdb_client.fetch(
            base, args["pdb_id"],
        ),
        "pdb_download": lambda args: pdb_client.download(
            base, args["pdb_id"], args.get("format", "pdb"),
        ),
        "alphafold_lookup": lambda args: alphafold_client.lookup(
            base, args["uniprot_accession"],
        ),
        "cath_classify": lambda args: cath_client.classify(
            base, args["domain_id"],
        ),
        "scop_classify": lambda args: scop_client.classify(
            base, args["pdb_id"],
        ),
    }


# ---------------------------------------------------------------------------
# StructuralServer
# ---------------------------------------------------------------------------


class StructuralServer(BaseLifeSciencesServer):
    """MCP server for structural biology databases.

    Databases covered: PDB, AlphaFold DB, CATH, SCOP.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-structural")
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
    """Start the structural biology MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    structural = StructuralServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await structural.server.run(
                read_stream,
                write_stream,
                structural.server.create_initialization_options(),
            )
    finally:
        await structural.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-structural``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
