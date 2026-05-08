"""Human Cell Atlas API client.

Base URL: https://service.azul.data.humancellatlas.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Cell Atlas"
BASE_URL = "https://service.azul.data.humancellatlas.org/"


async def search(
    server: BaseLifeSciencesServer,
    gene: str,
) -> dict[str, Any]:
    """Search Human Cell Atlas by gene symbol."""
    url = f"{BASE_URL}index/projects"
    params: dict[str, Any] = {
        "filters": f'{{"genusSpecies":{{"is":["Homo sapiens"]}}}}',
        "size": 10,
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=gene)
    return response.json()
