"""Roadmap Epigenomics API client.

Base URL: https://egg2.wustl.edu/roadmap/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Roadmap Epigenomics"
BASE_URL = "https://egg2.wustl.edu/roadmap/data/byFileType/"


async def search(
    server: BaseLifeSciencesServer,
    tissue: str,
    mark: str = "",
) -> dict[str, Any]:
    """Search Roadmap Epigenomics data by tissue and optional histone mark."""
    url = f"{BASE_URL}metadata.json"
    params: dict[str, Any] = {"tissue": tissue}
    if mark:
        params["mark"] = mark
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=tissue)
    return response.json()
