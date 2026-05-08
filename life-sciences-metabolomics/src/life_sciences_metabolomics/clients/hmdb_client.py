"""HMDB (Human Metabolome Database) API client.

Base URL: https://hmdb.ca/api/v1/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "HMDB"
BASE_URL = "https://hmdb.ca/api/v1/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search HMDB metabolites by name or identifier."""
    url = f"{BASE_URL}metabolites/search"
    params = {"query": query, "limit": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
