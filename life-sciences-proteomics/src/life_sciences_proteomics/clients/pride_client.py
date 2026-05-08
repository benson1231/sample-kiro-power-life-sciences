"""PRIDE Archive REST API client.

Base URL: https://www.ebi.ac.uk/pride/ws/archive/v2/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "PRIDE"
BASE_URL = "https://www.ebi.ac.uk/pride/ws/archive/v2/"


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search PRIDE proteomics projects by keyword."""
    url = f"{BASE_URL}search/projects"
    params: dict[str, Any] = {
        "keyword": keyword,
        "pageSize": max_results,
        "page": 0,
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    return response.json()
