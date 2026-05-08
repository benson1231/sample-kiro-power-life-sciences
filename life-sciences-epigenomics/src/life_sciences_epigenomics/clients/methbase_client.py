"""MethBase API client.

Base URL: http://smithlabresearch.org/methbase/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "MethBase"
BASE_URL = "http://smithlabresearch.org/methbase/api/"


async def search(
    server: BaseLifeSciencesServer,
    species: str,
    tissue: str = "",
) -> dict[str, Any]:
    """Search MethBase methylomes by species and optional tissue."""
    url = f"{BASE_URL}methylomes"
    params: dict[str, Any] = {"species": species}
    if tissue:
        params["tissue"] = tissue
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=species)
    return response.json()
