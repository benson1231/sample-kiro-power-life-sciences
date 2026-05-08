"""EMPIAR (Electron Microscopy Public Image Archive) API client.

Base URL: https://www.ebi.ac.uk/empiar/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "EMPIAR"
BASE_URL = "https://www.ebi.ac.uk/empiar/api/"


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
) -> dict[str, Any]:
    """Search EMPIAR entries by keyword."""
    url = f"{BASE_URL}entry/search"
    params: dict[str, Any] = {"q": keyword}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    return response.json()
