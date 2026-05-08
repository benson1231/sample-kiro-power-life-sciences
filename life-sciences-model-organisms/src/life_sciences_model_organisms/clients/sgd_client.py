"""SGD (Saccharomyces Genome Database) API client.

Base URL: https://www.yeastgenome.org/backend/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "SGD"
BASE_URL = "https://www.yeastgenome.org/backend/"

_JSON_HEADERS = {"Accept": "application/json"}


async def gene(
    server: BaseLifeSciencesServer,
    name: str,
) -> dict[str, Any]:
    """Lookup a gene by name in SGD."""
    url = f"{BASE_URL}locus/{name}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=name)
    return response.json()
