"""CARD (Comprehensive Antibiotic Resistance Database) API client.

Base URL: https://card.mcmaster.ca/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "CARD"
BASE_URL = "https://card.mcmaster.ca/api/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search CARD for antibiotic resistance genes."""
    url = f"{BASE_URL}search"
    params = {"q": query, "limit": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()


async def analyze(
    server: BaseLifeSciencesServer,
    sequence: str,
) -> dict[str, Any]:
    """Analyze a DNA sequence for antibiotic resistance genes using CARD."""
    url = f"{BASE_URL}blast"
    data = {"sequence": sequence}
    response = await server._request_with_retry(
        "POST", url, data=data, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=sequence[:50])
    return response.json()
