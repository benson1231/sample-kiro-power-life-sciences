"""MassBank mass spectra database API client.

Base URL: https://massbank.eu/MassBank/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "MassBank"
BASE_URL = "https://massbank.eu/MassBank/api/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search MassBank mass spectra by compound name or formula."""
    url = f"{BASE_URL}records/search"
    params = {"query": query, "limit": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
