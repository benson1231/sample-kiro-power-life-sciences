"""Greengenes taxonomy database API client.

Base URL: https://greengenes.secondgenome.com/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Greengenes"
BASE_URL = "https://greengenes.secondgenome.com/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
) -> dict[str, Any]:
    """Search Greengenes taxonomy database."""
    url = f"{BASE_URL}api/search"
    params = {"q": query}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
