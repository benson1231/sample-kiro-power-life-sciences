"""iNaturalist API client.

Base URL: https://api.inaturalist.org/v1/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "iNaturalist"
BASE_URL = "https://api.inaturalist.org/v1/"


async def search(
    server: BaseLifeSciencesServer,
    taxon: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search iNaturalist observations by taxon name."""
    url = f"{BASE_URL}observations"
    params: dict[str, Any] = {"taxon_name": taxon, "per_page": max_results}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=taxon)
    return response.json()
