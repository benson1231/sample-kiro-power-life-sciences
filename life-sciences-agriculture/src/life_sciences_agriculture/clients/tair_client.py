"""TAIR (The Arabidopsis Information Resource) API client.

Base URL: https://www.arabidopsis.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "TAIR"
BASE_URL = "https://www.arabidopsis.org/api/"


async def search(
    server: BaseLifeSciencesServer,
    query: str,
) -> dict[str, Any]:
    """Search TAIR Arabidopsis data by keyword."""
    url = f"{BASE_URL}search"
    params: dict[str, Any] = {"q": query}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
