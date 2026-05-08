"""MG-RAST metagenomics API client.

Base URL: https://api.mg-rast.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "MG-RAST"
BASE_URL = "https://api.mg-rast.org/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search MG-RAST metagenomes by keyword."""
    url = f"{BASE_URL}search"
    params = {"query": keyword, "limit": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    return response.json()
