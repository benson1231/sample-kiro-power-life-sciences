"""IDR (Image Data Resource) API client.

Base URL: https://idr.openmicroscopy.org/api/v0/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "IDR"
BASE_URL = "https://idr.openmicroscopy.org/api/v0/"


async def search(
    server: BaseLifeSciencesServer,
    query: str,
) -> dict[str, Any]:
    """Search IDR datasets by query string."""
    url = f"{BASE_URL}m/screens/"
    params: dict[str, Any] = {"search": query}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
