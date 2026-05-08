"""Genomics MCP server entry point.

Creates a ``GenomicsServer`` that extends :class:`BaseLifeSciencesServer`
and registers all genomics tools.  The server is started via stdio
transport when run as ``uvx life-sciences-genomics``.
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
    clinvar_client,
    cosmic_client,
    dbsnp_client,
    ddbj_client,
    encode_client,
    ensembl_client,
    geo_sra_client,
    gnomad_client,
    ncbi_client,
    thousand_genomes_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # NCBI
    Tool(
        name="ncbi_search",
        description="Search any NCBI database via Entrez esearch.",
        inputSchema={
            "type": "object",
            "properties": {
                "database": {
                    "type": "string",
                    "description": "NCBI database name (e.g. 'gene', 'nucleotide', 'protein').",
                },
                "term": {"type": "string", "description": "Search query string."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 20,
                },
            },
            "required": ["database", "term"],
        },
    ),
    Tool(
        name="ncbi_fetch_sequence",
        description="Fetch a nucleotide sequence by accession via Entrez efetch.",
        inputSchema={
            "type": "object",
            "properties": {
                "accession": {"type": "string", "description": "NCBI accession number."},
                "format": {
                    "type": "string",
                    "description": "Output format ('fasta' or 'gb').",
                    "default": "fasta",
                },
            },
            "required": ["accession"],
        },
    ),
    Tool(
        name="ncbi_pubmed_search",
        description="Search PubMed and return article summaries.",
        inputSchema={
            "type": "object",
            "properties": {
                "term": {"type": "string", "description": "PubMed search query."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum articles to return.",
                    "default": 10,
                },
            },
            "required": ["term"],
        },
    ),
    # Ensembl
    Tool(
        name="ensembl_gene_lookup",
        description="Lookup a gene by symbol and species via Ensembl REST.",
        inputSchema={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Gene symbol (e.g. 'BRCA2')."},
                "species": {
                    "type": "string",
                    "description": "Species name.",
                    "default": "homo_sapiens",
                },
            },
            "required": ["symbol"],
        },
    ),
    Tool(
        name="ensembl_variants",
        description="Get variants in a genomic region via Ensembl REST.",
        inputSchema={
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Genomic region (e.g. '7:140424943-140624564')."},
                "species": {"type": "string", "description": "Species name.", "default": "homo_sapiens"},
            },
            "required": ["region"],
        },
    ),
    Tool(
        name="ensembl_sequence",
        description="Get nucleotide sequence for a genomic region via Ensembl REST.",
        inputSchema={
            "type": "object",
            "properties": {
                "region": {"type": "string", "description": "Genomic region."},
                "species": {"type": "string", "description": "Species name.", "default": "homo_sapiens"},
            },
            "required": ["region"],
        },
    ),
    # ClinVar
    Tool(
        name="clinvar_search",
        description="Search ClinVar by rsID, HGVS notation, or gene name.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term (rsID, HGVS, or gene name)."},
                "max_results": {"type": "integer", "description": "Maximum results.", "default": 10},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="clinvar_get_variation",
        description="Get a full ClinVar variation record by variation ID.",
        inputSchema={
            "type": "object",
            "properties": {
                "variation_id": {"type": "string", "description": "ClinVar variation ID."},
            },
            "required": ["variation_id"],
        },
    ),
    # GEO / SRA
    Tool(
        name="geo_search",
        description="Search GEO datasets by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "term": {"type": "string", "description": "Search keyword."},
                "max_results": {"type": "integer", "description": "Maximum results.", "default": 10},
            },
            "required": ["term"],
        },
    ),
    Tool(
        name="geo_get_dataset",
        description="Get a GEO dataset by accession (e.g. GSE12345).",
        inputSchema={
            "type": "object",
            "properties": {
                "accession": {"type": "string", "description": "GEO accession number."},
            },
            "required": ["accession"],
        },
    ),
    Tool(
        name="sra_search",
        description="Search SRA runs by keyword or BioProject.",
        inputSchema={
            "type": "object",
            "properties": {
                "term": {"type": "string", "description": "Search keyword or BioProject accession."},
                "max_results": {"type": "integer", "description": "Maximum results.", "default": 10},
            },
            "required": ["term"],
        },
    ),
    # COSMIC
    Tool(
        name="cosmic_search",
        description="Search COSMIC somatic mutations by gene name. Requires COSMIC_API_KEY.",
        inputSchema={
            "type": "object",
            "properties": {
                "gene": {"type": "string", "description": "Gene symbol (e.g. 'BRAF')."},
            },
            "required": ["gene"],
        },
    ),
    # gnomAD
    Tool(
        name="gnomad_variant",
        description="Get allele frequency data for a variant from gnomAD.",
        inputSchema={
            "type": "object",
            "properties": {
                "variant_id": {"type": "string", "description": "Variant identifier (e.g. '1-55516888-G-A')."},
            },
            "required": ["variant_id"],
        },
    ),
    # dbSNP
    Tool(
        name="dbsnp_lookup",
        description="Lookup a variant by rsID from dbSNP.",
        inputSchema={
            "type": "object",
            "properties": {
                "rsid": {"type": "string", "description": "dbSNP rsID (e.g. 'rs328')."},
            },
            "required": ["rsid"],
        },
    ),
    # ENCODE
    Tool(
        name="encode_search",
        description="Search ENCODE experiments by biosample, assay, and/or target.",
        inputSchema={
            "type": "object",
            "properties": {
                "biosample": {"type": "string", "description": "Biosample term name.", "default": ""},
                "assay": {"type": "string", "description": "Assay title.", "default": ""},
                "target": {"type": "string", "description": "Target label.", "default": ""},
            },
        },
    ),
    # 1000 Genomes
    Tool(
        name="thousand_genomes_frequency",
        description="Get population allele frequencies from 1000 Genomes.",
        inputSchema={
            "type": "object",
            "properties": {
                "variant": {"type": "string", "description": "Variant identifier (e.g. 'rs56116432')."},
                "species": {"type": "string", "description": "Species name.", "default": "homo_sapiens"},
            },
            "required": ["variant"],
        },
    ),
    # DDBJ
    Tool(
        name="ddbj_search",
        description="Search DDBJ by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword."},
                "max_results": {"type": "integer", "description": "Maximum results.", "default": 10},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="ddbj_fetch_sequence",
        description="Fetch a sequence from DDBJ in FASTA format.",
        inputSchema={
            "type": "object",
            "properties": {
                "accession": {"type": "string", "description": "DDBJ accession number."},
            },
            "required": ["accession"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------

_TOOL_DISPATCH: dict[str, Any] = {}


def _build_dispatch(base: "GenomicsServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "ncbi_search": lambda args: ncbi_client.search(
            base, args["database"], args["term"], args.get("max_results", 20),
        ),
        "ncbi_fetch_sequence": lambda args: ncbi_client.fetch_sequence(
            base, args["accession"], args.get("format", "fasta"),
        ),
        "ncbi_pubmed_search": lambda args: ncbi_client.pubmed_search(
            base, args["term"], args.get("max_results", 10),
        ),
        "ensembl_gene_lookup": lambda args: ensembl_client.gene_lookup(
            base, args["symbol"], args.get("species", "homo_sapiens"),
        ),
        "ensembl_variants": lambda args: ensembl_client.variants(
            base, args["region"], args.get("species", "homo_sapiens"),
        ),
        "ensembl_sequence": lambda args: ensembl_client.sequence(
            base, args["region"], args.get("species", "homo_sapiens"),
        ),
        "clinvar_search": lambda args: clinvar_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "clinvar_get_variation": lambda args: clinvar_client.get_variation(
            base, args["variation_id"],
        ),
        "geo_search": lambda args: geo_sra_client.geo_search(
            base, args["term"], args.get("max_results", 10),
        ),
        "geo_get_dataset": lambda args: geo_sra_client.geo_get_dataset(
            base, args["accession"],
        ),
        "sra_search": lambda args: geo_sra_client.sra_search(
            base, args["term"], args.get("max_results", 10),
        ),
        "cosmic_search": lambda args: cosmic_client.search(
            base, args["gene"],
        ),
        "gnomad_variant": lambda args: gnomad_client.variant(
            base, args["variant_id"],
        ),
        "dbsnp_lookup": lambda args: dbsnp_client.lookup(
            base, args["rsid"],
        ),
        "encode_search": lambda args: encode_client.search(
            base, args.get("biosample", ""), args.get("assay", ""), args.get("target", ""),
        ),
        "thousand_genomes_frequency": lambda args: thousand_genomes_client.frequency(
            base, args["variant"], args.get("species", "homo_sapiens"),
        ),
        "ddbj_search": lambda args: ddbj_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "ddbj_fetch_sequence": lambda args: ddbj_client.fetch_sequence(
            base, args["accession"],
        ),
    }


# ---------------------------------------------------------------------------
# GenomicsServer
# ---------------------------------------------------------------------------


class GenomicsServer(BaseLifeSciencesServer):
    """MCP server for genomics and sequencing databases.

    Databases covered: NCBI, Ensembl, ClinVar, GEO, SRA, COSMIC,
    gnomAD, dbSNP, ENCODE, 1000 Genomes, DDBJ.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-genomics")
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
    """Start the genomics MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    genomics = GenomicsServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await genomics.server.run(
                read_stream,
                write_stream,
                genomics.server.create_initialization_options(),
            )
    finally:
        await genomics.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-genomics``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
