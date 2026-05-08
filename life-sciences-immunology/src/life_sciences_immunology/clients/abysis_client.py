"""abYsis antibody analysis API client.

Base URL: https://www.abysis.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "abYsis"
BASE_URL = "https://www.abysis.org/api/"

_JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}


async def analyze(
    server: BaseLifeSciencesServer,
    sequence: str,
) -> dict[str, Any]:
    """Analyze an antibody sequence using abYsis."""
    url = f"{BASE_URL}analyze"
    payload = {"sequence": sequence}
    response = await server._request_with_retry(
        "POST", url, json=payload, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=sequence[:50])
    return response.json()
