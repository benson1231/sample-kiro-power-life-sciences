"""NCBI BioSample API client.

Base URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BioSample"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


async def search(
    server: BaseLifeSciencesServer,
    query: str,
) -> dict[str, Any]:
    """Search NCBI BioSample database by keyword."""
    url = f"{BASE_URL}esearch.fcgi"
    params: dict[str, Any] = {
        "db": "biosample",
        "term": query,
        "retmax": 20,
        "retmode": "json",
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
