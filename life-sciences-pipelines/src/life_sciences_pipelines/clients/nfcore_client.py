"""nf-core pipeline registry client.

Base URL: https://nf-co.re/pipelines.json
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "nf-core"
BASE_URL = "https://nf-co.re/"


async def list_pipelines(
    server: BaseLifeSciencesServer,
    max_results: int = 20,
) -> dict[str, Any]:
    """List available nf-core pipelines."""
    url = f"{BASE_URL}pipelines.json"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME)
    data = response.json()
    pipelines = data.get("remote_workflows", [])[:max_results]
    return {"pipelines": pipelines, "count": len(pipelines)}


async def get_pipeline(
    server: BaseLifeSciencesServer,
    name: str,
) -> dict[str, Any]:
    """Get details for a specific nf-core pipeline."""
    url = f"{BASE_URL}pipelines.json"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=name)
    data = response.json()
    for pipeline in data.get("remote_workflows", []):
        if pipeline.get("name", "").lower() == name.lower():
            return pipeline
    return {"error": f"Pipeline '{name}' not found", "name": name}
