"""FDA FAERS (FDA Adverse Event Reporting System) API client.

Base URL: https://api.fda.gov/drug/event.json
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "FDA FAERS"
BASE_URL = "https://api.fda.gov/drug/event.json"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    drug: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search FDA FAERS adverse events by drug name."""
    params = {
        "search": f"patient.drug.openfda.generic_name:{drug}",
        "limit": max_results,
    }
    response = await server._request_with_retry(
        "GET", BASE_URL, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=drug)
    return response.json()
