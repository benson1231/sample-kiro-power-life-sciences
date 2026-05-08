"""NCBI Entrez API client.

Base URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "NCBI"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _api_key_params() -> dict[str, str]:
    """Return api_key param if NCBI_API_KEY is set."""
    key = os.environ.get("NCBI_API_KEY")
    if key:
        return {"api_key": key}
    return {}


async def search(
    server: BaseLifeSciencesServer,
    database: str,
    term: str,
    max_results: int = 20,
) -> dict[str, Any]:
    """Search any NCBI database via Entrez esearch."""
    params: dict[str, Any] = {
        "db": database,
        "term": term,
        "retmax": max_results,
        "retmode": "json",
        **_api_key_params(),
    }
    url = f"{BASE_URL}esearch.fcgi"
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=term)
    return response.json()


async def fetch_sequence(
    server: BaseLifeSciencesServer,
    accession: str,
    fmt: str = "fasta",
) -> dict[str, Any]:
    """Fetch a sequence by accession via Entrez efetch."""
    params: dict[str, Any] = {
        "db": "nucleotide",
        "id": accession,
        "rettype": fmt,
        "retmode": "text",
        **_api_key_params(),
    }
    url = f"{BASE_URL}efetch.fcgi"
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=accession)
    return {"accession": accession, "format": fmt, "data": response.text}


async def pubmed_search(
    server: BaseLifeSciencesServer,
    term: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search PubMed and return article summaries."""
    # Step 1: search for IDs
    search_params: dict[str, Any] = {
        "db": "pubmed",
        "term": term,
        "retmax": max_results,
        "retmode": "json",
        **_api_key_params(),
    }
    search_url = f"{BASE_URL}esearch.fcgi"
    search_resp = await server._request_with_retry("GET", search_url, params=search_params)
    await server._handle_api_error(search_resp, SERVICE_NAME, query=term)
    search_data = search_resp.json()

    id_list = search_data.get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return {"term": term, "count": 0, "articles": []}

    # Step 2: fetch summaries
    summary_params: dict[str, Any] = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "json",
        **_api_key_params(),
    }
    summary_url = f"{BASE_URL}esummary.fcgi"
    summary_resp = await server._request_with_retry("GET", summary_url, params=summary_params)
    await server._handle_api_error(summary_resp, SERVICE_NAME, query=term)
    summary_data = summary_resp.json()

    return {
        "term": term,
        "count": len(id_list),
        "articles": summary_data.get("result", {}),
    }
