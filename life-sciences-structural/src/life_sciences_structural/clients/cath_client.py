"""CATH Protein Structure Classification API client.

Base URL: https://www.cathdb.info/api/rest/id/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "CATH"
BASE_URL = "https://www.cathdb.info/api/rest/id"

_JSON_HEADERS = {"Accept": "application/json"}


async def classify(
    server: BaseLifeSciencesServer,
    domain_id: str,
) -> dict[str, Any]:
    """Get CATH domain classification by domain ID."""
    url = f"{BASE_URL}/{domain_id}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=domain_id)
    return response.json()
