"""RCSB PDB API client.

Search API: https://search.rcsb.org/rcsbsearch/v2/query
Data API:   https://data.rcsb.org/rest/v1/core/entry/{pdb_id}
Files:      https://files.rcsb.org/download/{pdb_id}.{format}
"""

from __future__ import annotations

import json
from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "PDB"
SEARCH_URL = "https://search.rcsb.org/rcsbsearch/v2/query"
DATA_URL = "https://data.rcsb.org/rest/v1/core/entry"
FILES_URL = "https://files.rcsb.org/download"

_JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search PDB structures by keyword."""
    payload = {
        "query": {
            "type": "terminal",
            "service": "full_text",
            "parameters": {"value": query},
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {"start": 0, "rows": max_results},
        },
    }
    response = await server._request_with_retry(
        "POST",
        SEARCH_URL,
        headers=_JSON_HEADERS,
        content=json.dumps(payload),
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()


async def fetch(
    server: BaseLifeSciencesServer,
    pdb_id: str,
) -> dict[str, Any]:
    """Fetch structure metadata by PDB ID."""
    url = f"{DATA_URL}/{pdb_id.upper()}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=pdb_id)
    return response.json()


async def download(
    server: BaseLifeSciencesServer,
    pdb_id: str,
    format: str = "pdb",
) -> dict[str, Any]:
    """Download a structure file in the specified format."""
    url = f"{FILES_URL}/{pdb_id.upper()}.{format}"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=pdb_id)
    return {"pdb_id": pdb_id, "format": format, "data": response.text}
