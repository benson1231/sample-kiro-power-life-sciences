"""WormBase REST API client.

Base URL: https://wormbase.org/rest/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "WormBase"
BASE_URL = "https://wormbase.org/rest/"

_JSON_HEADERS = {"Accept": "application/json"}


async def gene(
    server: BaseLifeSciencesServer,
    name: str,
) -> dict[str, Any]:
    """Lookup a gene by name in WormBase."""
    url = f"{BASE_URL}field/gene/{name}/overview"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=name)
    return response.json()
