"""IHEC (International Human Epigenome Consortium) API client.

Base URL: https://epigenomesportal.ca/ihec/api/v2/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "IHEC"
BASE_URL = "https://epigenomesportal.ca/ihec/api/v2/"


async def search(
    server: BaseLifeSciencesServer,
    tissue: str,
) -> dict[str, Any]:
    """Search IHEC datasets by tissue type."""
    url = f"{BASE_URL}datasets.json"
    params: dict[str, Any] = {"tissue": tissue}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=tissue)
    return response.json()
