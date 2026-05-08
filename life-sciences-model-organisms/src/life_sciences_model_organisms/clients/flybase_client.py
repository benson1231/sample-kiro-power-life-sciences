"""FlyBase API client.

Base URL: https://api.flybase.org/api/v1.0/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "FlyBase"
BASE_URL = "https://api.flybase.org/api/v1.0/"

_JSON_HEADERS = {"Accept": "application/json"}


async def gene(
    server: BaseLifeSciencesServer,
    symbol: str,
) -> dict[str, Any]:
    """Lookup a gene by symbol in FlyBase."""
    url = f"{BASE_URL}gene/{symbol}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=symbol)
    return response.json()
