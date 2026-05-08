"""OpenNeuro API client.

Base URL: https://openneuro.org/crn/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "OpenNeuro"
BASE_URL = "https://openneuro.org/crn/"


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
) -> dict[str, Any]:
    """Search OpenNeuro neuroimaging datasets by keyword."""
    url = f"{BASE_URL}datasets"
    params: dict[str, Any] = {"q": keyword}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    return response.json()
