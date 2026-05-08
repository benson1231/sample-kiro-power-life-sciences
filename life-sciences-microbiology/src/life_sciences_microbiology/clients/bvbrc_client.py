"""BV-BRC (Bacterial and Viral Bioinformatics Resource Center) API client.

Base URL: https://www.bv-brc.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BV-BRC"
BASE_URL = "https://www.bv-brc.org/api/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search BV-BRC genomes."""
    url = f"{BASE_URL}genome/"
    params = {"q": query, "limit": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()


async def features(
    server: BaseLifeSciencesServer,
    genome_id: str,
) -> dict[str, Any]:
    """Get features for a specific genome."""
    url = f"{BASE_URL}genome_feature/"
    params = {"eq(genome_id,{})".format(genome_id): "", "limit": 100}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=genome_id)
    return response.json()
