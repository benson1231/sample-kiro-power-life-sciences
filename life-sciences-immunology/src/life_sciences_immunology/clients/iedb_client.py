"""IEDB (Immune Epitope Database) API client.

Base URL: https://query-api.iedb.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "IEDB"
BASE_URL = "https://query-api.iedb.org/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    antigen: str,
    organism: str = "",
    max_results: int = 10,
) -> dict[str, Any]:
    """Search IEDB for epitopes by antigen name."""
    url = f"{BASE_URL}epitope_search"
    params: dict[str, Any] = {
        "linear_sequence": antigen,
        "limit": max_results,
    }
    if organism:
        params["source_organism"] = organism
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=antigen)
    return response.json()
