"""ClinVar API client (via NCBI Entrez).

Base URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ClinVar"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _api_key_params() -> dict[str, str]:
    key = os.environ.get("NCBI_API_KEY")
    if key:
        return {"api_key": key}
    return {}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search ClinVar by rsID, HGVS notation, or gene name."""
    params: dict[str, Any] = {
        "db": "clinvar",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        **_api_key_params(),
    }
    url = f"{BASE_URL}esearch.fcgi"
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()


async def get_variation(
    server: BaseLifeSciencesServer,
    variation_id: str,
) -> dict[str, Any]:
    """Get a full ClinVar variation record by ID."""
    params: dict[str, Any] = {
        "db": "clinvar",
        "id": variation_id,
        "retmode": "json",
        **_api_key_params(),
    }
    url = f"{BASE_URL}esummary.fcgi"
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=variation_id)
    return response.json()
