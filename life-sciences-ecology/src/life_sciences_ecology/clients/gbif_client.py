"""GBIF (Global Biodiversity Information Facility) API client.

Base URL: https://api.gbif.org/v1/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "GBIF"
BASE_URL = "https://api.gbif.org/v1/"


async def occurrences(
    server: BaseLifeSciencesServer,
    species: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search GBIF species occurrences."""
    url = f"{BASE_URL}occurrence/search"
    params: dict[str, Any] = {"scientificName": species, "limit": max_results}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=species)
    return response.json()


async def taxonomy(
    server: BaseLifeSciencesServer,
    species: str,
) -> dict[str, Any]:
    """Search GBIF taxonomy by species name."""
    url = f"{BASE_URL}species/match"
    params: dict[str, Any] = {"name": species}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=species)
    return response.json()
