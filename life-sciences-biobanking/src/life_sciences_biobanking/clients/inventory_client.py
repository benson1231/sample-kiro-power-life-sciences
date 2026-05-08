"""Sample inventory management client.

Provides sample inventory search and tracking.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Sample Inventory"
BASE_URL = "https://inventory.example.org/api/v1/"


async def search(
    server: BaseLifeSciencesServer,
    sample_type: str = "",
    location: str = "",
) -> dict[str, Any]:
    """Search sample inventory by type and/or location."""
    url = f"{BASE_URL}samples"
    params: dict[str, Any] = {}
    if sample_type:
        params["type"] = sample_type
    if location:
        params["location"] = location
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=sample_type or location)
    return response.json()
