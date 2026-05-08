"""IMGT (ImMunoGeneTics) API client.

Base URL: https://www.imgt.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "IMGT"
BASE_URL = "https://www.imgt.org/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    gene: str,
    species: str = "Homo sapiens",
) -> dict[str, Any]:
    """Search IMGT for immunoglobulin/T-cell receptor gene information."""
    url = f"{BASE_URL}genedb/GENElect"
    params = {
        "query": "7.1",
        "species": species,
        "IMGTlabel": gene,
    }
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=gene)
    # IMGT returns HTML; extract key info
    text = response.text
    return {
        "gene": gene,
        "species": species,
        "source": "IMGT",
        "raw_content": text[:3000],
    }
