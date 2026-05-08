"""Proteomics MCP server entry point.

Creates a ``ProteomicsServer`` that extends :class:`BaseLifeSciencesServer`
and registers all proteomics tools.  The server is started via stdio
transport when run as ``uvx life-sciences-proteomics``.
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
    interpro_client,
    nextprot_client,
    pfam_client,
    pride_client,
    string_client,
    uniprot_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # UniProt
    Tool(
        name="uniprot_search",
        description="Search UniProt by protein or gene name.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Protein or gene name to search for.",
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
        name="uniprot_fetch",
        description="Fetch a full protein record by UniProt accession.",
        inputSchema={
            "type": "object",
            "properties": {
                "accession": {
                    "type": "string",
                    "description": "UniProt accession (e.g. 'P04637').",
                },
            },
            "required": ["accession"],
        },
    ),
    Tool(
        name="uniprot_sequence",
        description="Get amino acid sequence in FASTA format by UniProt accession.",
        inputSchema={
            "type": "object",
            "properties": {
                "accession": {
                    "type": "string",
                    "description": "UniProt accession (e.g. 'P04637').",
                },
            },
            "required": ["accession"],
        },
    ),
    # InterPro
    Tool(
        name="interpro_lookup",
        description="Query InterPro by protein accession or domain ID (e.g. 'IPR000719').",
        inputSchema={
            "type": "object",
            "properties": {
                "accession": {
                    "type": "string",
                    "description": "Protein accession or InterPro domain ID.",
                },
            },
            "required": ["accession"],
        },
    ),
    # Pfam
    Tool(
        name="pfam_family",
        description="Query Pfam by family identifier (e.g. 'PF00069').",
        inputSchema={
            "type": "object",
            "properties": {
                "family_id": {
                    "type": "string",
                    "description": "Pfam family identifier (e.g. 'PF00069').",
                },
            },
            "required": ["family_id"],
        },
    ),
    # STRING
    Tool(
        name="string_interactions",
        description="Get protein-protein interactions from STRING.",
        inputSchema={
            "type": "object",
            "properties": {
                "protein": {
                    "type": "string",
                    "description": "Protein name or identifier (e.g. 'TP53').",
                },
                "species": {
                    "type": "integer",
                    "description": "NCBI taxonomy ID (default 9606 for Homo sapiens).",
                    "default": 9606,
                },
            },
            "required": ["protein"],
        },
    ),
    # PRIDE
    Tool(
        name="pride_search",
        description="Search PRIDE proteomics projects by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search keyword.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["keyword"],
        },
    ),
    # neXtProt
    Tool(
        name="nextprot_entry",
        description="Get a human protein entry by gene name from neXtProt.",
        inputSchema={
            "type": "object",
            "properties": {
                "gene_name": {
                    "type": "string",
                    "description": "Gene name (e.g. 'TP53').",
                },
            },
            "required": ["gene_name"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "ProteomicsServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "uniprot_search": lambda args: uniprot_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "uniprot_fetch": lambda args: uniprot_client.fetch(
            base, args["accession"],
        ),
        "uniprot_sequence": lambda args: uniprot_client.sequence(
            base, args["accession"],
        ),
        "interpro_lookup": lambda args: interpro_client.lookup(
            base, args["accession"],
        ),
        "pfam_family": lambda args: pfam_client.family(
            base, args["family_id"],
        ),
        "string_interactions": lambda args: string_client.interactions(
            base, args["protein"], args.get("species", 9606),
        ),
        "pride_search": lambda args: pride_client.search(
            base, args["keyword"], args.get("max_results", 10),
        ),
        "nextprot_entry": lambda args: nextprot_client.entry(
            base, args["gene_name"],
        ),
    }


# ---------------------------------------------------------------------------
# ProteomicsServer
# ---------------------------------------------------------------------------


class ProteomicsServer(BaseLifeSciencesServer):
    """MCP server for proteomics databases.

    Databases covered: UniProt, InterPro, Pfam, STRING, PRIDE, neXtProt.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-proteomics")
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
    """Start the proteomics MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    proteomics = ProteomicsServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await proteomics.server.run(
                read_stream,
                write_stream,
                proteomics.server.create_initialization_options(),
            )
    finally:
        await proteomics.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-proteomics``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
