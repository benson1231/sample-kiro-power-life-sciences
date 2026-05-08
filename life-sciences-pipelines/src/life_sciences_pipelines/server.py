"""Pipelines MCP server entry point.

Creates a ``PipelinesServer`` that extends :class:`BaseLifeSciencesServer`
and registers all pipeline registry tools.  The server is started via stdio
transport when run as ``uvx life-sciences-pipelines``.
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
    cwl_client,
    github_client,
    nfcore_client,
    wdl_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="nfcore_list",
        description="List available nf-core Nextflow pipelines.",
        inputSchema={
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum pipelines to return.",
                    "default": 20,
                },
            },
        },
    ),
    Tool(
        name="nfcore_pipeline",
        description="Get details for a specific nf-core pipeline.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Pipeline name (e.g. 'rnaseq', 'sarek')."},
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="wdl_list",
        description="List available WDL pipelines (GATK best practices).",
        inputSchema={
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum pipelines to return.",
                    "default": 20,
                },
            },
        },
    ),
    Tool(
        name="wdl_pipeline",
        description="Get details for a specific WDL pipeline.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Pipeline name."},
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="cwl_list",
        description="List available CWL pipelines.",
        inputSchema={
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum pipelines to return.",
                    "default": 20,
                },
            },
        },
    ),
    Tool(
        name="cwl_pipeline",
        description="Get details for a specific CWL pipeline.",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Pipeline name."},
            },
            "required": ["name"],
        },
    ),
    Tool(
        name="github_pipelines",
        description="Search GitHub for bioinformatics pipelines by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword."},
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return.",
                    "default": 20,
                },
            },
            "required": ["keyword"],
        },
    ),
    Tool(
        name="pipeline_healthomics_import",
        description="Generate AWS HealthOmics import instructions for a pipeline.",
        inputSchema={
            "type": "object",
            "properties": {
                "pipeline_name": {"type": "string", "description": "Pipeline repository name (e.g. 'nf-core/rnaseq')."},
                "workflow_language": {"type": "string", "description": "Workflow language ('nextflow', 'wdl', 'cwl')."},
            },
            "required": ["pipeline_name", "workflow_language"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "PipelinesServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "nfcore_list": lambda args: nfcore_client.list_pipelines(
            base, args.get("max_results", 20),
        ),
        "nfcore_pipeline": lambda args: nfcore_client.get_pipeline(
            base, args["name"],
        ),
        "wdl_list": lambda args: wdl_client.list_pipelines(
            base, args.get("max_results", 20),
        ),
        "wdl_pipeline": lambda args: wdl_client.get_pipeline(
            base, args["name"],
        ),
        "cwl_list": lambda args: cwl_client.list_pipelines(
            base, args.get("max_results", 20),
        ),
        "cwl_pipeline": lambda args: cwl_client.get_pipeline(
            base, args["name"],
        ),
        "github_pipelines": lambda args: github_client.search_pipelines(
            base, args["keyword"], args.get("max_results", 20),
        ),
        "pipeline_healthomics_import": lambda args: github_client.healthomics_import(
            base, args["pipeline_name"], args["workflow_language"],
        ),
    }


# ---------------------------------------------------------------------------
# PipelinesServer
# ---------------------------------------------------------------------------


class PipelinesServer(BaseLifeSciencesServer):
    """MCP server for bioinformatics pipeline registries.

    Registries covered: nf-core, WDL (GATK), CWL, GitHub community.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-pipelines")
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
    """Start the pipelines MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    pipelines = PipelinesServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await pipelines.server.run(
                read_stream,
                write_stream,
                pipelines.server.create_initialization_options(),
            )
    finally:
        await pipelines.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-pipelines``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
