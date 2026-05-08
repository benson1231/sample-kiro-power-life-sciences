"""MGI (Mouse Genome Informatics) API client.

Base URL: https://www.informatics.jax.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "MGI"
BASE_URL = "https://www.informatics.jax.org/api/"

_JSON_HEADERS = {"Accept": "application/json"}


async def gene(
    server: BaseLifeSciencesServer,
    symbol: str,
) -> dict[str, Any]:
    """Lookup a gene by symbol in MGI."""
    url = f"{BASE_URL}marker/{symbol}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=symbol)
    return response.json()
