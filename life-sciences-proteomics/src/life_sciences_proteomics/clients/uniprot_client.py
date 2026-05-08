"""UniProt REST API client.

Base URL: https://rest.uniprot.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "UniProt"
BASE_URL = "https://rest.uniprot.org/"


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search UniProt by protein or gene name."""
    url = f"{BASE_URL}uniprotkb/search"
    params: dict[str, Any] = {
        "query": query,
        "size": max_results,
        "format": "json",
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()


async def fetch(
    server: BaseLifeSciencesServer,
    accession: str,
) -> dict[str, Any]:
    """Fetch a full protein record by UniProt accession."""
    url = f"{BASE_URL}uniprotkb/{accession}.json"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=accession)
    return response.json()


async def sequence(
    server: BaseLifeSciencesServer,
    accession: str,
) -> dict[str, Any]:
    """Get amino acid sequence in FASTA format by UniProt accession."""
    url = f"{BASE_URL}uniprotkb/{accession}.fasta"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=accession)
    return {"accession": accession, "format": "fasta", "data": response.text}
