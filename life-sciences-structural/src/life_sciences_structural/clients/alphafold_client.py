"""AlphaFold Protein Structure Database API client.

Base URL: https://alphafold.ebi.ac.uk/api/prediction/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "AlphaFold DB"
BASE_URL = "https://alphafold.ebi.ac.uk/api/prediction"

_JSON_HEADERS = {"Accept": "application/json"}


async def lookup(
    server: BaseLifeSciencesServer,
    uniprot_accession: str,
) -> dict[str, Any]:
    """Get predicted structure by UniProt accession."""
    url = f"{BASE_URL}/{uniprot_accession}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=uniprot_accession)
    data = response.json()
    # The API returns a list; return the first (latest) prediction
    if isinstance(data, list) and data:
        return data[0]
    return data
