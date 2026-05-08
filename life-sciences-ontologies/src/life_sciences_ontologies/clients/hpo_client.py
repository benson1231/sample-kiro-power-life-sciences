"""Human Phenotype Ontology (HPO) API client.

Base URL: https://hpo.jax.org/api/hpo/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "HPO"
BASE_URL = "https://hpo.jax.org/api/hpo"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    term: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search HPO phenotype terms by keyword."""
    url = f"{BASE_URL}/search"
    params = {"q": term, "max": max_results}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=term)
    return response.json()


async def get_term(
    server: BaseLifeSciencesServer,
    hpo_id: str,
) -> dict[str, Any]:
    """Get HPO term details by HPO ID (e.g. 'HP:0001250')."""
    url = f"{BASE_URL}/term/{hpo_id}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=hpo_id)
    return response.json()
