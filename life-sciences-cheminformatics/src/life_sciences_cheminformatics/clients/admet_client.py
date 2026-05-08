"""ADMETlab ADMET prediction API client.

Base URL: https://admetmesh.scbdd.com/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ADMETlab"
BASE_URL = "https://admetmesh.scbdd.com/api/"

_JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}


async def predict(
    server: BaseLifeSciencesServer,
    smiles: str,
) -> dict[str, Any]:
    """Predict ADMET properties for a compound."""
    url = f"{BASE_URL}predict"
    payload = {"smiles": smiles}
    response = await server._request_with_retry(
        "POST", url, json=payload, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=smiles)
    return response.json()
