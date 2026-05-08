"""Disease Ontology API client.

Base URL: https://www.disease-ontology.org/api/metadata/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Disease Ontology"
BASE_URL = "https://www.disease-ontology.org/api/metadata"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    term: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search Disease Ontology by term."""
    url = f"{BASE_URL}/DO:{term}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=term)
    return response.json()
