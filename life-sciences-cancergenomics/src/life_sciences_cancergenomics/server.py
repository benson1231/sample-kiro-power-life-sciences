"""Cancer genomics MCP server entry point.

Creates a ``CancerGenomicsServer`` that extends
:class:`BaseLifeSciencesServer` and registers all cBioPortal tools. The
server is started via stdio transport when run as
``uvx life-sciences-cancergenomics``.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from mcp.types import TextContent, Tool

from life_sciences_common import BaseLifeSciencesServer

from .clients import cbioportal_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="cbioportal_search_studies",
        description=(
            "Search for cancer genomics studies by keyword. "
            "Examples: 'melanoma', 'breast cancer', 'TCGA', 'immunotherapy'."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Keyword to match against study id, name, or description.",
                },
            },
            "required": ["keyword"],
        },
    ),
    Tool(
        name="cbioportal_get_study_details",
        description=(
            "Get detailed information about a cBioPortal study including "
            "molecular profiles and sample lists."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "study_id": {
                    "type": "string",
                    "description": "cBioPortal study identifier (e.g. 'skcm_tcga').",
                },
            },
            "required": ["study_id"],
        },
    ),
    Tool(
        name="cbioportal_get_molecular_profiles",
        description=(
            "List available molecular data types for a study — mutations, "
            "copy number, expression, methylation."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "study_id": {
                    "type": "string",
                    "description": "cBioPortal study identifier.",
                },
            },
            "required": ["study_id"],
        },
    ),
    Tool(
        name="cbioportal_get_clinical_data",
        description=(
            "Get clinical data for samples in a study. Omit attribute_id to "
            "list available clinical attributes."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "study_id": {
                    "type": "string",
                    "description": "cBioPortal study identifier.",
                },
                "attribute_id": {
                    "type": "string",
                    "description": "Clinical attribute id. Omit to list available attributes.",
                    "default": "",
                },
                "data_type": {
                    "type": "string",
                    "description": "Clinical data type ('SAMPLE' or 'PATIENT').",
                    "default": "SAMPLE",
                },
            },
            "required": ["study_id"],
        },
    ),
    Tool(
        name="cbioportal_search_genes",
        description=(
            "Search for gene information by symbol or alias. Returns Entrez "
            "gene ID, Hugo symbol, and type."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Gene symbol or alias (e.g. 'TP53').",
                },
            },
            "required": ["keyword"],
        },
    ),
    Tool(
        name="cbioportal_compare_mutation_burden",
        description=(
            "Compare tumor mutation burden across samples in a study. High "
            "TMB tumors are better candidates for neoantigen vaccines."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "study_id": {
                    "type": "string",
                    "description": "cBioPortal study identifier.",
                },
            },
            "required": ["study_id"],
        },
    ),
    Tool(
        name="cbioportal_list_cancer_types",
        description="List all cancer types available in cBioPortal.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "CancerGenomicsServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "cbioportal_search_studies": lambda args: cbioportal_client.search_studies(
            base, args["keyword"],
        ),
        "cbioportal_get_study_details": lambda args: cbioportal_client.get_study_details(
            base, args["study_id"],
        ),
        "cbioportal_get_molecular_profiles": lambda args: cbioportal_client.get_molecular_profiles(
            base, args["study_id"],
        ),
        "cbioportal_get_clinical_data": lambda args: cbioportal_client.get_clinical_data(
            base,
            args["study_id"],
            args.get("attribute_id", ""),
            args.get("data_type", "SAMPLE"),
        ),
        "cbioportal_search_genes": lambda args: cbioportal_client.search_genes(
            base, args["keyword"],
        ),
        "cbioportal_compare_mutation_burden": lambda args: cbioportal_client.compare_mutation_burden(
            base, args["study_id"],
        ),
        "cbioportal_list_cancer_types": lambda args: cbioportal_client.list_cancer_types(
            base,
        ),
    }


# ---------------------------------------------------------------------------
# CancerGenomicsServer
# ---------------------------------------------------------------------------


class CancerGenomicsServer(BaseLifeSciencesServer):
    """MCP server for cancer genomics data from cBioPortal.

    Provides study search, molecular profiles, clinical data, gene lookups,
    cancer type browsing, and tumor mutation burden analysis.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-cancergenomics")
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
    """Start the cancer genomics MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    cancer = CancerGenomicsServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await cancer.server.run(
                read_stream,
                write_stream,
                cancer.server.create_initialization_options(),
            )
    finally:
        await cancer.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-cancergenomics``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
