"""DDBJ API client.

Base URL: https://ddbj.nig.ac.jp/services/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "DDBJ"
BASE_URL = "https://ddbj.nig.ac.jp/services/"


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search DDBJ by keyword."""
    url = f"{BASE_URL}arsa/search"
    params: dict[str, Any] = {
        "query": query,
        "limit": max_results,
        "format": "json",
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()


async def fetch_sequence(
    server: BaseLifeSciencesServer,
    accession: str,
) -> dict[str, Any]:
    """Fetch a sequence from DDBJ in FASTA format."""
    url = f"{BASE_URL}arsa/get/{accession}"
    params = {"format": "fasta"}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=accession)
    return {"accession": accession, "format": "fasta", "data": response.text}
