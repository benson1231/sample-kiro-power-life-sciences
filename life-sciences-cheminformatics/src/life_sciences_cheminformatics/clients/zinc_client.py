"""ZINC database API client.

Base URL: https://zinc15.docking.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ZINC"
BASE_URL = "https://zinc15.docking.org/api/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    smiles: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search ZINC compounds by SMILES string."""
    url = f"{BASE_URL}substances/search/"
    params = {"q": smiles, "count": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=smiles)
    return response.json()
