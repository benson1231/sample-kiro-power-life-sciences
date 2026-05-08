"""IntAct Molecular Interaction Database API client.

Base URL: https://www.ebi.ac.uk/intact/ws/interaction/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "IntAct"
BASE_URL = "https://www.ebi.ac.uk/intact/ws/interaction"

_JSON_HEADERS = {"Accept": "application/json"}


async def interactions(
    server: BaseLifeSciencesServer,
    protein: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Get molecular interactions for a protein from IntAct."""
    url = f"{BASE_URL}/findInteractor/{protein}"
    params = {"pageSize": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=protein)
    return response.json()
