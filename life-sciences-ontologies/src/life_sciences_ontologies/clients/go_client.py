"""Gene Ontology API client.

Base URL: https://api.geneontology.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Gene Ontology"
BASE_URL = "https://api.geneontology.org/api"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    term: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search Gene Ontology terms by keyword."""
    url = f"{BASE_URL}/search/entity/autocomplete/{term}"
    params = {"rows": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=term)
    return response.json()


async def get_term(
    server: BaseLifeSciencesServer,
    go_id: str,
) -> dict[str, Any]:
    """Get GO term details by GO ID (e.g. 'GO:0008150')."""
    url = f"{BASE_URL}/ontology/term/{go_id}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=go_id)
    return response.json()


async def annotations(
    server: BaseLifeSciencesServer,
    go_id: str,
    max_results: int = 20,
) -> dict[str, Any]:
    """Get gene annotations for a GO term."""
    url = f"{BASE_URL}/bioentity/function/{go_id}/genes"
    params = {"rows": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=go_id)
    return response.json()
