"""GenBank Environmental Sequences API client.

Uses NCBI Entrez to search environmental nucleotide sequences.
Base URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "GenBank Environmental"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


async def search(
    server: BaseLifeSciencesServer,
    query: str,
) -> dict[str, Any]:
    """Search GenBank environmental sequences by keyword."""
    url = f"{BASE_URL}esearch.fcgi"
    params: dict[str, Any] = {
        "db": "nuccore",
        "term": f"{query}[orgn] AND environmental sample[filter]",
        "retmax": 20,
        "retmode": "json",
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
