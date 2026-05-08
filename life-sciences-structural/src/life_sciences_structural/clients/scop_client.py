"""SCOP (Structural Classification of Proteins) API client.

Base URL: https://scop.mrc-lmb.cam.ac.uk/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "SCOP"
BASE_URL = "https://scop.mrc-lmb.cam.ac.uk/api"

_JSON_HEADERS = {"Accept": "application/json"}


async def classify(
    server: BaseLifeSciencesServer,
    pdb_id: str,
) -> dict[str, Any]:
    """Get SCOP structural classification by PDB ID."""
    url = f"{BASE_URL}/pdb/{pdb_id.lower()}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=pdb_id)
    return response.json()
