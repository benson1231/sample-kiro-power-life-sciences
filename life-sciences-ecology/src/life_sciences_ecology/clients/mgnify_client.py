"""MGnify (EBI Metagenomics) API client.

Base URL: https://www.ebi.ac.uk/metagenomics/api/v1/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "MGnify"
BASE_URL = "https://www.ebi.ac.uk/metagenomics/api/v1/"


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
) -> dict[str, Any]:
    """Search MGnify metagenomics studies by keyword."""
    url = f"{BASE_URL}studies"
    params: dict[str, Any] = {"search": keyword}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    return response.json()
