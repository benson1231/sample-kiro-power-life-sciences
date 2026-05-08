"""OMOP CDM (Observational Medical Outcomes Partnership) API client.

Base URL: https://athena.ohdsi.org/api/v1/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "OMOP CDM"
BASE_URL = "https://athena.ohdsi.org/api/v1/"


async def search(
    server: BaseLifeSciencesServer,
    concept: str,
) -> dict[str, Any]:
    """Search OMOP CDM concepts by keyword."""
    url = f"{BASE_URL}concepts"
    params: dict[str, Any] = {"query": concept, "pageSize": 20}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=concept)
    return response.json()
