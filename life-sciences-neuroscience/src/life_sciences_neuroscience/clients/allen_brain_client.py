"""Allen Brain Atlas API client.

Base URL: https://api.brain-map.org/api/v2/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Allen Brain Atlas"
BASE_URL = "https://api.brain-map.org/api/v2/"


async def search(
    server: BaseLifeSciencesServer,
    gene: str,
) -> dict[str, Any]:
    """Search Allen Brain Atlas gene expression data by gene symbol."""
    url = f"{BASE_URL}data/query.json"
    params: dict[str, Any] = {
        "criteria": f"model::Gene,rma::criteria,[acronym$eq'{gene}']",
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=gene)
    return response.json()


async def structure(
    server: BaseLifeSciencesServer,
    structure_id: str,
) -> dict[str, Any]:
    """Get Allen Brain Atlas structure information by ID."""
    url = f"{BASE_URL}data/Structure/{structure_id}.json"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=structure_id)
    return response.json()
