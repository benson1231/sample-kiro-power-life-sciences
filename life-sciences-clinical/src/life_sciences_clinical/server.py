"""Clinical and Pharma MCP server entry point.

Creates a ``ClinicalServer`` that extends :class:`BaseLifeSciencesServer`
and registers all clinical and pharma tools.  The server is started via stdio
transport when run as ``uvx life-sciences-clinical``.
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
    chembl_client,
    clinicaltrials_client,
    drugbank_client,
    fda_faers_client,
    omim_client,
    opentargets_client,
    pharmgkb_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # OMIM (auth required)
    Tool(
        name="omim_search",
        description="Search OMIM genetic disorder entries. Requires OMIM_API_KEY.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'Marfan syndrome').",
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
        name="omim_entry",
        description="Get OMIM entry by MIM number. Requires OMIM_API_KEY.",
        inputSchema={
            "type": "object",
            "properties": {
                "mim_number": {
                    "type": "string",
                    "description": "MIM number (e.g. '154700').",
                },
            },
            "required": ["mim_number"],
        },
    ),
    # DrugBank (auth required)
    Tool(
        name="drugbank_search",
        description="Search DrugBank drugs by keyword. Requires DRUGBANK_API_KEY.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'aspirin').",
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
        name="drugbank_drug",
        description="Get drug details by DrugBank ID. Requires DRUGBANK_API_KEY.",
        inputSchema={
            "type": "object",
            "properties": {
                "drugbank_id": {
                    "type": "string",
                    "description": "DrugBank identifier (e.g. 'DB00945').",
                },
            },
            "required": ["drugbank_id"],
        },
    ),
    # ChEMBL
    Tool(
        name="chembl_search",
        description="Search ChEMBL compounds by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'ibuprofen').",
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
        name="chembl_bioactivity",
        description="Get bioactivity data for a ChEMBL compound.",
        inputSchema={
            "type": "object",
            "properties": {
                "chembl_id": {
                    "type": "string",
                    "description": "ChEMBL compound identifier (e.g. 'CHEMBL25').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 100,
                },
            },
            "required": ["chembl_id"],
        },
    ),
    # PharmGKB
    Tool(
        name="pharmgkb_search",
        description="Search PharmGKB pharmacogenomics data by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'warfarin', 'CYP2D6').",
                },
            },
            "required": ["query"],
        },
    ),
    # OpenTargets
    Tool(
        name="opentargets_search",
        description="Search Open Targets for drug targets and disease associations.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search keyword (e.g. 'BRAF', 'lung cancer').",
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
    # FDA FAERS
    Tool(
        name="fda_faers_search",
        description="Search FDA FAERS adverse event reports by drug name.",
        inputSchema={
            "type": "object",
            "properties": {
                "drug": {
                    "type": "string",
                    "description": "Drug generic name (e.g. 'aspirin').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["drug"],
        },
    ),
    # ClinicalTrials.gov
    Tool(
        name="clinicaltrials_search",
        description="Search ClinicalTrials.gov by condition.",
        inputSchema={
            "type": "object",
            "properties": {
                "condition": {
                    "type": "string",
                    "description": "Condition or disease (e.g. 'breast cancer').",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["condition"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "ClinicalServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "omim_search": lambda args: omim_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "omim_entry": lambda args: omim_client.entry(
            base, args["mim_number"],
        ),
        "drugbank_search": lambda args: drugbank_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "drugbank_drug": lambda args: drugbank_client.drug(
            base, args["drugbank_id"],
        ),
        "chembl_search": lambda args: chembl_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "chembl_bioactivity": lambda args: chembl_client.bioactivity(
            base, args["chembl_id"], args.get("max_results", 100),
        ),
        "pharmgkb_search": lambda args: pharmgkb_client.search(
            base, args["query"],
        ),
        "opentargets_search": lambda args: opentargets_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "fda_faers_search": lambda args: fda_faers_client.search(
            base, args["drug"], args.get("max_results", 10),
        ),
        "clinicaltrials_search": lambda args: clinicaltrials_client.search(
            base, args["condition"], args.get("max_results", 10),
        ),
    }


# ---------------------------------------------------------------------------
# ClinicalServer
# ---------------------------------------------------------------------------


class ClinicalServer(BaseLifeSciencesServer):
    """MCP server for clinical and pharmaceutical databases.

    Databases covered: OMIM, DrugBank, ChEMBL, PharmGKB, OpenTargets,
    FDA FAERS, ClinicalTrials.gov.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-clinical")
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
    """Start the clinical MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    clinical = ClinicalServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await clinical.server.run(
                read_stream,
                write_stream,
                clinical.server.create_initialization_options(),
            )
    finally:
        await clinical.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-clinical``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
