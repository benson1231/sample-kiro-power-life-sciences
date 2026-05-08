"""BioImage Archive API client.

Base URL: https://www.ebi.ac.uk/bioimage-archive/api/v1/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BioImage Archive"
BASE_URL = "https://www.ebi.ac.uk/bioimage-archive/api/v1/"


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
) -> dict[str, Any]:
    """Search BioImage Archive by keyword."""
    url = f"{BASE_URL}images/search"
    params: dict[str, Any] = {"query": keyword}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    return response.json()
