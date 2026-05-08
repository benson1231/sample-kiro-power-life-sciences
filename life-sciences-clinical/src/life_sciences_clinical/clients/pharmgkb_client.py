"""PharmGKB API client.

Base URL: https://api.pharmgkb.org/v1/data/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "PharmGKB"
BASE_URL = "https://api.pharmgkb.org/v1/data"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
) -> dict[str, Any]:
    """Search PharmGKB by keyword."""
    url = f"{BASE_URL}/search"
    params = {"query": query}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
