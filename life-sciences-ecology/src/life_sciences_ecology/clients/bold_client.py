"""BOLD (Barcode of Life Data System) API client.

Base URL: https://v3.boldsystems.org/index.php/API_Public/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BOLD"
BASE_URL = "https://v3.boldsystems.org/index.php/API_Public/"


async def search(
    server: BaseLifeSciencesServer,
    taxon: str,
) -> dict[str, Any]:
    """Search BOLD barcode records by taxon name."""
    url = f"{BASE_URL}combined"
    params: dict[str, Any] = {"taxon": taxon, "format": "json"}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=taxon)
    return response.json()
