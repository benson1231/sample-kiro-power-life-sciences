"""MetaboLights API client.

Base URL: https://www.ebi.ac.uk/metabolights/ws/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "MetaboLights"
BASE_URL = "https://www.ebi.ac.uk/metabolights/ws/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search MetaboLights studies by keyword."""
    url = f"{BASE_URL}studies/search"
    params = {"query": keyword, "limit": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    return response.json()
