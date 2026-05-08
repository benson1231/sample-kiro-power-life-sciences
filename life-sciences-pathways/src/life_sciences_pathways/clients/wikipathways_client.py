"""WikiPathways API client.

Base URL: https://webservice.wikipathways.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "WikiPathways"
BASE_URL = "https://webservice.wikipathways.org"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    organism: str = "Homo sapiens",
) -> dict[str, Any]:
    """Search WikiPathways by text query."""
    url = f"{BASE_URL}/findPathwaysByText"
    params = {"query": query, "species": organism, "format": "json"}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
