"""Reactome Pathway Database API client.

Base URL: https://reactome.org/ContentService/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Reactome"
BASE_URL = "https://reactome.org/ContentService"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search Reactome pathways by keyword."""
    url = f"{BASE_URL}/search/query"
    params = {"query": query, "types": "Pathway", "cluster": "true"}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    data = response.json()
    # Limit results
    if isinstance(data, dict) and "results" in data:
        for group in data.get("results", []):
            if "entries" in group:
                group["entries"] = group["entries"][:max_results]
    return data


async def pathway(
    server: BaseLifeSciencesServer,
    stable_id: str,
) -> dict[str, Any]:
    """Get Reactome pathway details by stable ID (e.g. 'R-HSA-1640170')."""
    url = f"{BASE_URL}/data/query/{stable_id}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=stable_id)
    return response.json()
