"""ClinicalTrials.gov API client.

Base URL: https://clinicaltrials.gov/api/v2/studies
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ClinicalTrials.gov"
BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    condition: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search ClinicalTrials.gov by condition."""
    params = {
        "query.cond": condition,
        "pageSize": max_results,
        "format": "json",
    }
    response = await server._request_with_retry(
        "GET", BASE_URL, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=condition)
    return response.json()
