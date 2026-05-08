"""Cloud and HPC MCP server entry point.

Creates a ``CloudServer`` that extends :class:`BaseLifeSciencesServer`
and registers all cloud/HPC tools.  The server is started via stdio
transport when run as ``uvx life-sciences-cloud``.
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
    aws_batch_client,
    galaxy_client,
    terra_client,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="aws_batch_submit",
        description="Submit a job to AWS Batch.",
        inputSchema={
            "type": "object",
            "properties": {
                "job_definition": {"type": "string", "description": "AWS Batch job definition name or ARN."},
                "queue": {"type": "string", "description": "AWS Batch job queue name or ARN."},
                "parameters": {
                    "type": "object",
                    "description": "Job parameters as key-value pairs.",
                },
            },
            "required": ["job_definition", "queue", "parameters"],
        },
    ),
    Tool(
        name="aws_batch_status",
        description="Get the status of an AWS Batch job.",
        inputSchema={
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "AWS Batch job ID."},
            },
            "required": ["job_id"],
        },
    ),
    Tool(
        name="terra_workspaces",
        description="List Terra workspaces. Requires TERRA_TOKEN.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="terra_submit",
        description="Submit a workflow to a Terra workspace. Requires TERRA_TOKEN.",
        inputSchema={
            "type": "object",
            "properties": {
                "workspace": {"type": "string", "description": "Terra workspace (namespace/name)."},
                "method": {"type": "string", "description": "Method configuration name."},
                "entity_set": {"type": "string", "description": "Entity set to process."},
            },
            "required": ["workspace", "method", "entity_set"],
        },
    ),
    Tool(
        name="galaxy_tools",
        description="List available Galaxy tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "server_url": {
                    "type": "string",
                    "description": "Galaxy server URL.",
                    "default": "https://usegalaxy.org",
                },
            },
        },
    ),
    Tool(
        name="galaxy_submit",
        description="Submit a Galaxy tool job.",
        inputSchema={
            "type": "object",
            "properties": {
                "server_url": {"type": "string", "description": "Galaxy server URL."},
                "tool_id": {"type": "string", "description": "Galaxy tool ID."},
                "inputs": {
                    "type": "object",
                    "description": "Tool input parameters.",
                },
            },
            "required": ["server_url", "tool_id", "inputs"],
        },
    ),
    Tool(
        name="galaxy_status",
        description="Get the status of a Galaxy job.",
        inputSchema={
            "type": "object",
            "properties": {
                "server_url": {"type": "string", "description": "Galaxy server URL."},
                "job_id": {"type": "string", "description": "Galaxy job ID."},
            },
            "required": ["server_url", "job_id"],
        },
    ),
]


# ---------------------------------------------------------------------------
# Tool dispatch
# ---------------------------------------------------------------------------


def _build_dispatch(base: "CloudServer") -> dict[str, Any]:
    """Build a name → coroutine-function mapping for all tools."""
    return {
        "aws_batch_submit": lambda args: aws_batch_client.submit(
            base, args["job_definition"], args["queue"], args["parameters"],
        ),
        "aws_batch_status": lambda args: aws_batch_client.status(
            base, args["job_id"],
        ),
        "terra_workspaces": lambda args: terra_client.workspaces(base),
        "terra_submit": lambda args: terra_client.submit(
            base, args["workspace"], args["method"], args["entity_set"],
        ),
        "galaxy_tools": lambda args: galaxy_client.tools(
            base, args.get("server_url", "https://usegalaxy.org"),
        ),
        "galaxy_submit": lambda args: galaxy_client.submit(
            base, args["server_url"], args["tool_id"], args["inputs"],
        ),
        "galaxy_status": lambda args: galaxy_client.status(
            base, args["server_url"], args["job_id"],
        ),
    }


# ---------------------------------------------------------------------------
# CloudServer
# ---------------------------------------------------------------------------


class CloudServer(BaseLifeSciencesServer):
    """MCP server for cloud and HPC platforms.

    Tools covered: AWS Batch, Terra, Galaxy.
    """

    def __init__(self) -> None:
        super().__init__("life-sciences-cloud")
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
    """Start the cloud MCP server over stdio."""
    from mcp.server.stdio import stdio_server

    cloud = CloudServer()
    try:
        async with stdio_server() as (read_stream, write_stream):
            await cloud.server.run(
                read_stream,
                write_stream,
                cloud.server.create_initialization_options(),
            )
    finally:
        await cloud.cleanup()


def main() -> None:
    """CLI entry point for ``life-sciences-cloud``."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
