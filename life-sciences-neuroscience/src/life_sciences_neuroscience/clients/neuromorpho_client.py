"""NeuroMorpho.Org API client.

Base URL: https://neuromorpho.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "NeuroMorpho"
BASE_URL = "https://neuromorpho.org/api/"


async def search(
    server: BaseLifeSciencesServer,
    cell_type: str,
    brain_region: str = "",
) -> dict[str, Any]:
    """Search NeuroMorpho neuron morphologies by cell type and optional brain region."""
    url = f"{BASE_URL}neuron/select"
    params: dict[str, Any] = {"q": f"cell_type:{cell_type}"}
    if brain_region:
        params["q"] += f" AND brain_region:{brain_region}"
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=cell_type)
    return response.json()
