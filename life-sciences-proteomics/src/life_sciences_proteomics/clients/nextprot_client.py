"""neXtProt REST API client.

Base URL: https://api.nextprot.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "neXtProt"
BASE_URL = "https://api.nextprot.org/"

_JSON_HEADERS = {"Accept": "application/json"}


async def entry(
    server: BaseLifeSciencesServer,
    gene_name: str,
) -> dict[str, Any]:
    """Get a human protein entry by gene name from neXtProt."""
    url = f"{BASE_URL}entry/NX_{gene_name}.json"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=gene_name)
    return response.json()
