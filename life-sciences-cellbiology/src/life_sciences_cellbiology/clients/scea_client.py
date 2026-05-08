"""Single Cell Expression Atlas (SCEA) API client.

Base URL: https://www.ebi.ac.uk/gxa/sc/json/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Single Cell Expression Atlas"
BASE_URL = "https://www.ebi.ac.uk/gxa/sc/json/"


async def search(
    server: BaseLifeSciencesServer,
    gene: str,
    species: str = "",
) -> dict[str, Any]:
    """Search Single Cell Expression Atlas by gene and optional species."""
    url = f"{BASE_URL}search"
    params: dict[str, Any] = {"geneQuery": gene}
    if species:
        params["species"] = species
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=gene)
    return response.json()
