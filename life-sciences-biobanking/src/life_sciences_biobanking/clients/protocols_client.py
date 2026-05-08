"""protocols.io API client.

Base URL: https://www.protocols.io/api/v4/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "protocols.io"
BASE_URL = "https://www.protocols.io/api/v4/"


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
) -> dict[str, Any]:
    """Search protocols.io for laboratory protocols by keyword."""
    url = f"{BASE_URL}protocols"
    params: dict[str, Any] = {"key": keyword}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    return response.json()
