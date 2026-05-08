"""GEO and SRA API client (via NCBI Entrez).

Base URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME_GEO = "GEO"
SERVICE_NAME_SRA = "SRA"
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _api_key_params() -> dict[str, str]:
    key = os.environ.get("NCBI_API_KEY")
    if key:
        return {"api_key": key}
    return {}


async def geo_search(
    server: BaseLifeSciencesServer,
    term: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search GEO datasets by keyword."""
    params: dict[str, Any] = {
        "db": "gds",
        "term": term,
        "retmax": max_results,
        "retmode": "json",
        **_api_key_params(),
    }
    url = f"{BASE_URL}esearch.fcgi"
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME_GEO, query=term)
    return response.json()


async def geo_get_dataset(
    server: BaseLifeSciencesServer,
    accession: str,
) -> dict[str, Any]:
    """Get a GEO dataset by accession (e.g. GSE12345)."""
    params: dict[str, Any] = {
        "db": "gds",
        "term": accession,
        "retmax": 1,
        "retmode": "json",
        **_api_key_params(),
    }
    url = f"{BASE_URL}esearch.fcgi"
    search_resp = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(search_resp, SERVICE_NAME_GEO, query=accession)
    search_data = search_resp.json()
    id_list = search_data.get("esearchresult", {}).get("idlist", [])
    if not id_list:
        return {"accession": accession, "found": False, "data": {}}

    summary_params: dict[str, Any] = {
        "db": "gds",
        "id": ",".join(id_list),
        "retmode": "json",
        **_api_key_params(),
    }
    summary_url = f"{BASE_URL}esummary.fcgi"
    summary_resp = await server._request_with_retry("GET", summary_url, params=summary_params)
    await server._handle_api_error(summary_resp, SERVICE_NAME_GEO, query=accession)
    return {"accession": accession, "found": True, "data": summary_resp.json()}


async def sra_search(
    server: BaseLifeSciencesServer,
    term: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search SRA runs by keyword or BioProject."""
    params: dict[str, Any] = {
        "db": "sra",
        "term": term,
        "retmax": max_results,
        "retmode": "json",
        **_api_key_params(),
    }
    url = f"{BASE_URL}esearch.fcgi"
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME_SRA, query=term)
    return response.json()
