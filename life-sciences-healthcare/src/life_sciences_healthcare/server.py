"""Healthcare Standards MCP server entry point.

Creates a ``HealthcareServer`` that extends :class:`BaseLifeSciencesServer`
and registers all healthcare tools.  The server is started via stdio
transport when run as ``uvx life-sciences-healthcare``.
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
    dicomweb_client,
    fhir_client,
    hl7_client,
    omop_client,
    redcap_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="fhir_search",
        description="Search FHIR resources by type and parameters.",
        inputSchema={
            "type": "object",
            "properties": {
                "resource_type": {"type": "string", "description": "FHIR resource type (e.g. 'Patient', 'Observation')."},
                "params": {
                    "type": "object",
                    "description": "Search parameters as key-value pairs.",
                    "additionalProperties": {"type": "string"},
                },
            },
            "required": ["resource_type", "params"],
        },
    ),
    Tool(
        name="fhir_create",
        description="Create a FHIR resource.",
        inputSchema={
            "type": "object",
            "properties": {
                "resource_type": {"type": "string", "description": "FHIR resource type."},
                "resource": {
                    "type": "object",
                    "description": "FHIR resource JSON.",
                },
            },
            "required": ["resource_type", "resource"],
        },
    ),
    Tool(
        name="hl7_parse",
        description="Parse an HL7 v2 message into structured segments.",
        inputSchema={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Raw HL7 v2 message string."},
            },
            "required": ["message"],
        },
    ),
    Tool(
        name="hl7_generate",
        description="Generate an HL7 v2 message from structured data.",
        inputSchema={
            "type": "object",
            "properties": {
                "message_type": {"type": "string", "description": "HL7 message type (e.g. 'ADT^A01')."},
                "data": {
                    "type": "object",
                    "description": "Structured data for message generation.",
                },
            },
            "required": ["message_type", "data"],
        },
    ),
    Tool(
        name="omop_search",
        description="Search OMOP CDM concepts by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "concept": {"type": "string", "description": "Concept search term."},
            },
            "required": ["concept"],
        },
    ),
    Tool(
        name="redcap_records",
        description="Get REDCap records for a project. Requires REDCAP_API_TOKEN.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "REDCap project ID."},
                "filter": {
                    "type": "string",
                    "description": "Filter logic expression.",
                    "default": "",
                },
            },
            "required": ["project_id"],
        },
    ),
    Tool(
        name="redcap_export",
        description="Export REDCap project data. Requires REDCAP_API_TOKEN.",
        inputSchema={
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "description": "REDCap project ID."},
                "format": {
                    "type": "string",
                    "description": "Export format ('json', 'csv', 'xml').",
                    "default": "json",
                },
            },
            "required": ["project_id"],
        },
    ),
    Tool(
        name="dicomweb_query",
        description="Query DICOMweb studies by patient ID and/or study date.",
        inputSchema={
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "Patient ID.",
                    "default": "",
                },
                "study_date": {
                    "type": "string",
                    "description": "Study date (YYYYMMDD).",
                    "default": "",
                },
            },
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "HealthcareServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "fhir_search": lambda args: fhir_client.search(
            base, args["resource_type"], args["params"],
        ),
        "fhir_create": lambda args: fhir_client.create(
            base, args["resource_type"], args["resource"],
        ),
        "hl7_parse": lambda args: hl7_client.parse(
            base, args["message"],
        ),
        "hl7_generate": lambda args: hl7_client.generate(
            base, args["message_type"], args["data"],
        ),
        "omop_search": lambda args: omop_client.search(
            base, args["concept"],
        ),
        "redcap_records": lambda args: redcap_client.records(
            base, args["project_id"], args.get("filter", ""),
        ),
        "redcap_export": lambda args: redcap_client.export(
            base, args["project_id"], args.get("format", "json"),
        ),
        "dicomweb_query": lambda args: dicomweb_client.query(
            base, args.get("patient_id", ""), args.get("study_date", ""),
        ),
    }


# ---------------------------------------------------------------------------
# HealthcareServer
# ---------------------------------------------------------------------------


class HealthcareServer(BaseLifeSciencesServer):
    """MCP server for healthcare standards.

    Tools covered: FHIR, HL7 v2, OMOP CDM, REDCap, DICOMweb.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-healthcare")
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
    """Start the healthcare MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    healthcare = HealthcareServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await healthcare.server.run(
                read_stream,
                write_stream,
                healthcare.server.create_initialization_options(),
            )
    finally:
        await healthcare.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-healthcare``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
