"""BrainMap API client.

Base URL: https://brainmap.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BrainMap"
BASE_URL = "https://brainmap.org/api/"


async def search(
    server: BaseLifeSciencesServer,
    region: str,
) -> dict[str, Any]:
    """Search BrainMap functional neuroimaging data by brain region."""
    url = f"{BASE_URL}search"
    params: dict[str, Any] = {"region": region}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=region)
    return response.json()
