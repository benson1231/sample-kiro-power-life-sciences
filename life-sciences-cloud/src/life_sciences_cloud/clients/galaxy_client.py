"""Galaxy API client.

Default server URL: https://usegalaxy.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Galaxy"
DEFAULT_URL = "https://usegalaxy.org"


async def tools(
    server: BaseLifeSciencesServer,
    server_url: str = DEFAULT_URL,
) -> dict[str, Any]:
    """List available Galaxy tools."""
    url = f"{server_url.rstrip('/')}/api/tools"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME)
    return response.json()


async def submit(
    server: BaseLifeSciencesServer,
    server_url: str,
    tool_id: str,
    inputs: dict[str, Any],
) -> dict[str, Any]:
    """Submit a Galaxy tool job."""
    url = f"{server_url.rstrip('/')}/api/tools"
    payload = {"tool_id": tool_id, "inputs": inputs}
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=tool_id)
    return response.json()


async def status(
    server: BaseLifeSciencesServer,
    server_url: str,
    job_id: str,
) -> dict[str, Any]:
    """Get the status of a Galaxy job."""
    url = f"{server_url.rstrip('/')}/api/jobs/{job_id}"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=job_id)
    return response.json()
