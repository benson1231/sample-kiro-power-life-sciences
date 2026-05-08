"""ChEMBL API client.

Base URL: https://www.ebi.ac.uk/chembl/api/data/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ChEMBL"
BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search ChEMBL compounds by keyword."""
    url = f"{BASE_URL}/molecule/search"
    params = {"q": query, "limit": max_results, "format": "json"}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()


async def bioactivity(
    server: BaseLifeSciencesServer,
    chembl_id: str,
    max_results: int = 100,
) -> dict[str, Any]:
    """Get bioactivity data for a ChEMBL compound."""
    url = f"{BASE_URL}/activity"
    params = {
        "molecule_chembl_id": chembl_id,
        "limit": max_results,
        "format": "json",
    }
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=chembl_id)
    return response.json()
