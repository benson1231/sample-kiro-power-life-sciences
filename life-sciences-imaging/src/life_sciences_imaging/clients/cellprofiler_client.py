"""CellProfiler API client.

Provides pipeline execution interface for CellProfiler image analysis.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "CellProfiler"
BASE_URL = "https://cellprofiler.org/api/v1/"


async def run(
    server: BaseLifeSciencesServer,
    pipeline: str,
    images: list[str],
) -> dict[str, Any]:
    """Run a CellProfiler pipeline on a set of images."""
    url = f"{BASE_URL}pipelines/run"
    payload = {"pipeline": pipeline, "images": images}
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=pipeline)
    return response.json()
