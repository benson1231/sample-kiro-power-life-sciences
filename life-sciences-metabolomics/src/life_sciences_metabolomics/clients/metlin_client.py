"""METLIN metabolite mass spectrometry database API client.

Base URL: https://metlin.scripps.edu/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "METLIN"
BASE_URL = "https://metlin.scripps.edu/api/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    mass: float,
    tolerance: float = 0.01,
) -> dict[str, Any]:
    """Search METLIN by exact mass with tolerance."""
    url = f"{BASE_URL}search"
    params = {"mass": mass, "tolerance": tolerance}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=str(mass))
    return response.json()
