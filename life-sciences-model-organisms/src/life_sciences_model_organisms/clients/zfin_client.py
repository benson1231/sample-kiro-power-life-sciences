"""ZFIN API client.

Base URL: https://zfin.org/action/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ZFIN"
BASE_URL = "https://zfin.org/action/api/"

_JSON_HEADERS = {"Accept": "application/json"}


async def gene(
    server: BaseLifeSciencesServer,
    name: str,
) -> dict[str, Any]:
    """Lookup a gene by name in ZFIN."""
    url = f"{BASE_URL}search"
    params = {"q": name, "category": "Gene"}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=name)
    return response.json()
