"""Imaging and Microscopy MCP server entry point.

Creates an ``ImagingServer`` that extends :class:`BaseLifeSciencesServer`
and registers all imaging tools.  The server is started via stdio
transport when run as ``uvx life-sciences-imaging``.
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
    bioimage_client,
    cellprofiler_client,
    dicom_client,
    empiar_client,
    idr_client,
    imagej_client,
    omero_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="omero_search",
        description="Search OMERO images by query string.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="cellprofiler_run",
        description="Run a CellProfiler pipeline on a set of images.",
        inputSchema={
            "type": "object",
            "properties": {
                "pipeline": {"type": "string", "description": "Pipeline name or definition."},
                "images": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of image paths or URLs.",
                },
            },
            "required": ["pipeline", "images"],
        },
    ),
    Tool(
        name="imagej_macro",
        description="Run an ImageJ macro on an image.",
        inputSchema={
            "type": "object",
            "properties": {
                "macro": {"type": "string", "description": "ImageJ macro code."},
                "image": {"type": "string", "description": "Image path or URL."},
            },
            "required": ["macro", "image"],
        },
    ),
    Tool(
        name="dicom_query",
        description="Query DICOM studies by patient ID and/or modality.",
        inputSchema={
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "string",
                    "description": "Patient ID.",
                    "default": "",
                },
                "modality": {
                    "type": "string",
                    "description": "Imaging modality (e.g. 'CT', 'MR').",
                    "default": "",
                },
            },
        },
    ),
    Tool(
        name="bioimage_search",
        description="Search BioImage Archive by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword."},
            },
            "required": ["keyword"],
        },
    ),
    Tool(
        name="idr_search",
        description="Search IDR (Image Data Resource) datasets.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="empiar_search",
        description="Search EMPIAR electron microscopy entries by keyword.",
        inputSchema={
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword."},
            },
            "required": ["keyword"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "ImagingServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "omero_search": lambda args: omero_client.search(
            base, args["query"],
        ),
        "cellprofiler_run": lambda args: cellprofiler_client.run(
            base, args["pipeline"], args["images"],
        ),
        "imagej_macro": lambda args: imagej_client.macro(
            base, args["macro"], args["image"],
        ),
        "dicom_query": lambda args: dicom_client.query(
            base, args.get("patient_id", ""), args.get("modality", ""),
        ),
        "bioimage_search": lambda args: bioimage_client.search(
            base, args["keyword"],
        ),
        "idr_search": lambda args: idr_client.search(
            base, args["query"],
        ),
        "empiar_search": lambda args: empiar_client.search(
            base, args["keyword"],
        ),
    }


# ---------------------------------------------------------------------------
# ImagingServer
# ---------------------------------------------------------------------------


class ImagingServer(BaseLifeSciencesServer):
    """MCP server for imaging and microscopy tools.

    Tools covered: OMERO, CellProfiler, ImageJ, DICOM,
    BioImage Archive, IDR, EMPIAR.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-imaging")
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
    """Start the imaging MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    imaging = ImagingServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await imaging.server.run(
                read_stream,
                write_stream,
                imaging.server.create_initialization_options(),
            )
    finally:
        await imaging.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-imaging``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
