"""Molecular Biology and Biochemistry MCP server entry point.

Creates a ``MolBioServer`` that extends :class:`BaseLifeSciencesServer`
and registers all molecular biology tools.  The server is started via stdio
transport when run as ``uvx life-sciences-molbio``.
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
    blast_client,
    hmmer_client,
    msa_client,
    primer_client,
    rebase_client,
    restriction_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # BLAST
    Tool(
        name="blast_search",
        description="Submit a BLAST sequence search to NCBI.",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "Nucleotide or protein sequence."},
                "database": {
                    "type": "string",
                    "description": "BLAST database (e.g. 'nr', 'nt', 'refseq_rna').",
                    "default": "nr",
                },
                "program": {
                    "type": "string",
                    "description": "BLAST program (e.g. 'blastn', 'blastp', 'blastx').",
                    "default": "blastn",
                },
            },
            "required": ["sequence"],
        },
    ),
    Tool(
        name="blast_results",
        description="Get BLAST results by request ID (RID).",
        inputSchema={
            "type": "object",
            "properties": {
                "rid": {"type": "string", "description": "BLAST request ID from blast_search."},
            },
            "required": ["rid"],
        },
    ),
    # MSA
    Tool(
        name="msa_align",
        description="Submit a multiple sequence alignment job (Clustal Omega or MUSCLE).",
        inputSchema={
            "type": "object",
            "properties": {
                "sequences": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of sequences (FASTA format or raw).",
                },
                "tool": {
                    "type": "string",
                    "description": "Alignment tool ('clustalo' or 'muscle').",
                    "default": "clustalo",
                },
            },
            "required": ["sequences"],
        },
    ),
    # HMMER
    Tool(
        name="hmmer_search",
        description="Search a protein sequence against HMMER databases (e.g. Pfam).",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "Protein sequence."},
                "database": {
                    "type": "string",
                    "description": "Target database (e.g. 'pfam', 'tigrfam').",
                    "default": "pfam",
                },
            },
            "required": ["sequence"],
        },
    ),
    # Primer3
    Tool(
        name="primer3_design",
        description="Design PCR primers for a template sequence using Primer3.",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "Template DNA sequence."},
                "product_size_min": {
                    "type": "integer",
                    "description": "Minimum PCR product size.",
                    "default": 100,
                },
                "product_size_max": {
                    "type": "integer",
                    "description": "Maximum PCR product size.",
                    "default": 300,
                },
            },
            "required": ["sequence"],
        },
    ),
    Tool(
        name="primer_blast",
        description="Check primer specificity using Primer-BLAST.",
        inputSchema={
            "type": "object",
            "properties": {
                "forward": {"type": "string", "description": "Forward primer sequence."},
                "reverse": {"type": "string", "description": "Reverse primer sequence."},
                "organism": {
                    "type": "string",
                    "description": "Target organism.",
                    "default": "Homo sapiens",
                },
            },
            "required": ["forward", "reverse"],
        },
    ),
    # Restriction analysis
    Tool(
        name="restriction_analysis",
        description="Find restriction enzyme cut sites in a DNA sequence.",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence": {"type": "string", "description": "DNA sequence to analyze."},
                "enzymes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of enzyme names to check. If omitted, checks all common enzymes.",
                },
            },
            "required": ["sequence"],
        },
    ),
    # REBASE
    Tool(
        name="rebase_enzyme",
        description="Lookup restriction enzyme information from REBASE.",
        inputSchema={
            "type": "object",
            "properties": {
                "enzyme_name": {"type": "string", "description": "Restriction enzyme name (e.g. 'EcoRI')."},
            },
            "required": ["enzyme_name"],
        },
    ),
    # Cloning design
    Tool(
        name="cloning_design",
        description="Design a cloning strategy with specified restriction sites.",
        inputSchema={
            "type": "object",
            "properties": {
                "vector": {"type": "string", "description": "Vector DNA sequence."},
                "insert": {"type": "string", "description": "Insert DNA sequence."},
                "sites": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Restriction enzyme names to use for cloning.",
                },
            },
            "required": ["vector", "insert", "sites"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "MolBioServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "blast_search": lambda args: blast_client.search(
            base, args["sequence"], args.get("database", "nr"), args.get("program", "blastn"),
        ),
        "blast_results": lambda args: blast_client.results(
            base, args["rid"],
        ),
        "msa_align": lambda args: msa_client.align(
            base, args["sequences"], args.get("tool", "clustalo"),
        ),
        "hmmer_search": lambda args: hmmer_client.search(
            base, args["sequence"], args.get("database", "pfam"),
        ),
        "primer3_design": lambda args: primer_client.design(
            base, args["sequence"], args.get("product_size_min", 100), args.get("product_size_max", 300),
        ),
        "primer_blast": lambda args: primer_client.blast(
            base, args["forward"], args["reverse"], args.get("organism", "Homo sapiens"),
        ),
        "restriction_analysis": lambda args: restriction_client.analysis(
            base, args["sequence"], args.get("enzymes"),
        ),
        "rebase_enzyme": lambda args: rebase_client.enzyme(
            base, args["enzyme_name"],
        ),
        "cloning_design": lambda args: restriction_client.cloning_design(
            base, args["vector"], args["insert"], args["sites"],
        ),
    }


# ---------------------------------------------------------------------------
# MolBioServer
# ---------------------------------------------------------------------------


class MolBioServer(BaseLifeSciencesServer):
    """MCP server for molecular biology and biochemistry tools.

    Tools covered: BLAST, MSA (Clustal Omega/MUSCLE), HMMER, Primer3,
    Primer-BLAST, restriction analysis, REBASE, cloning design.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-molbio")
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
    """Start the molecular biology MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    molbio = MolBioServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await molbio.server.run(
                read_stream,
                write_stream,
                molbio.server.create_initialization_options(),
            )
    finally:
        await molbio.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-molbio``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
