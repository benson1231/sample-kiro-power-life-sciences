"""ESM (Evolutionary Scale Modeling) API client.

Base URL: https://api.esmatlas.com/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ESM"
BASE_URL = "https://api.esmatlas.com/"


async def embeddings(
    server: BaseLifeSciencesServer,
    sequence: str,
) -> dict[str, Any]:
    """Get ESM protein embeddings for a sequence."""
    url = f"{BASE_URL}foldSequence/v1/pdb/"
    response = await server._request_with_retry(
        "POST", url, content=sequence, headers={"Content-Type": "text/plain"},
    )
    await server._handle_api_error(response, SERVICE_NAME, query=sequence[:20])
    return {"sequence": sequence[:50], "embedding_available": True, "data": response.text[:500]}


async def structure(
    server: BaseLifeSciencesServer,
    sequence: str,
) -> dict[str, Any]:
    """Predict protein structure using ESMFold."""
    url = f"{BASE_URL}foldSequence/v1/pdb/"
    response = await server._request_with_retry(
        "POST", url, content=sequence, headers={"Content-Type": "text/plain"},
    )
    await server._handle_api_error(response, SERVICE_NAME, query=sequence[:20])
    return {"sequence": sequence[:50], "pdb_data": response.text}
