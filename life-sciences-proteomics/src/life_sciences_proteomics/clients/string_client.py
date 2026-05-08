"""STRING (Search Tool for Retrieval of Interacting Genes/Proteins) API client.

Base URL: https://string-db.org/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "STRING"
BASE_URL = "https://string-db.org/api/"


async def interactions(
    server: BaseLifeSciencesServer,
    protein: str,
    species: int = 9606,
) -> dict[str, Any]:
    """Get protein-protein interactions from STRING.

    Parameters
    ----------
    protein:
        Protein name or identifier (e.g. ``"TP53"``).
    species:
        NCBI taxonomy ID for the organism (default ``9606`` for *Homo sapiens*).
    """
    url = f"{BASE_URL}json/network"
    params: dict[str, Any] = {
        "identifiers": protein,
        "species": species,
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=protein)
    return {"protein": protein, "species": species, "interactions": response.json()}
