"""Cheminformatics MCP server entry point.

Creates a ``CheminformaticsServer`` that extends :class:`BaseLifeSciencesServer`
and registers all cheminformatics tools.  The server is started via stdio
transport when run as ``uvx life-sciences-cheminformatics``.
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
    admet_client,
    chemspider_client,
    docking_client,
    pubchem_client,
    rdkit_client,
    zinc_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    # PubChem
    Tool(
        name="pubchem_search",
        description="Search PubChem compounds by name or SMILES.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Compound name or SMILES string."},
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
        name="pubchem_properties",
        description="Get compound properties by PubChem CID.",
        inputSchema={
            "type": "object",
            "properties": {
                "cid": {"type": "string", "description": "PubChem compound ID."},
            },
            "required": ["cid"],
        },
    ),
    # ChemSpider
    Tool(
        name="chemspider_search",
        description="Search ChemSpider compounds by name. Requires CHEMSPIDER_API_KEY.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Compound name or formula."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    ),
    # ZINC
    Tool(
        name="zinc_search",
        description="Search ZINC commercially available compounds by SMILES.",
        inputSchema={
            "type": "object",
            "properties": {
                "smiles": {"type": "string", "description": "SMILES string to search."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 10,
                },
            },
            "required": ["smiles"],
        },
    ),
    # RDKit
    Tool(
        name="rdkit_descriptors",
        description="Compute molecular descriptors from a SMILES string.",
        inputSchema={
            "type": "object",
            "properties": {
                "smiles": {"type": "string", "description": "SMILES string."},
            },
            "required": ["smiles"],
        },
    ),
    Tool(
        name="rdkit_substructure",
        description="Search for a SMARTS substructure pattern in a list of molecules.",
        inputSchema={
            "type": "object",
            "properties": {
                "smarts": {"type": "string", "description": "SMARTS substructure pattern."},
                "molecules": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of SMILES strings to search.",
                },
            },
            "required": ["smarts", "molecules"],
        },
    ),
    # Docking
    Tool(
        name="docking_submit",
        description="Submit a molecular docking job to SwissDock.",
        inputSchema={
            "type": "object",
            "properties": {
                "receptor_pdb": {"type": "string", "description": "PDB ID or PDB content of the receptor."},
                "ligand_smiles": {"type": "string", "description": "SMILES string of the ligand."},
            },
            "required": ["receptor_pdb", "ligand_smiles"],
        },
    ),
    # ADMET
    Tool(
        name="admet_predict",
        description="Predict ADMET (absorption, distribution, metabolism, excretion, toxicity) properties.",
        inputSchema={
            "type": "object",
            "properties": {
                "smiles": {"type": "string", "description": "SMILES string of the compound."},
            },
            "required": ["smiles"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "CheminformaticsServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "pubchem_search": lambda args: pubchem_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "pubchem_properties": lambda args: pubchem_client.properties(
            base, args["cid"],
        ),
        "chemspider_search": lambda args: chemspider_client.search(
            base, args["query"], args.get("max_results", 10),
        ),
        "zinc_search": lambda args: zinc_client.search(
            base, args["smiles"], args.get("max_results", 10),
        ),
        "rdkit_descriptors": lambda args: rdkit_client.descriptors(
            base, args["smiles"],
        ),
        "rdkit_substructure": lambda args: rdkit_client.substructure(
            base, args["smarts"], args["molecules"],
        ),
        "docking_submit": lambda args: docking_client.submit(
            base, args["receptor_pdb"], args["ligand_smiles"],
        ),
        "admet_predict": lambda args: admet_client.predict(
            base, args["smiles"],
        ),
    }


# ---------------------------------------------------------------------------
# CheminformaticsServer
# ---------------------------------------------------------------------------


class CheminformaticsServer(BaseLifeSciencesServer):
    """MCP server for computational chemistry and drug discovery.

    Tools covered: PubChem, ChemSpider, ZINC, RDKit descriptors,
    RDKit substructure search, SwissDock docking, ADMET prediction.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-cheminformatics")
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
    """Start the cheminformatics MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    cheminformatics = CheminformaticsServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await cheminformatics.server.run(
                read_stream,
                write_stream,
                cheminformatics.server.create_initialization_options(),
            )
    finally:
        await cheminformatics.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-cheminformatics``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
