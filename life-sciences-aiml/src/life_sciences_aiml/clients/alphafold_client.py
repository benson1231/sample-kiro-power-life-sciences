"""AlphaFold prediction API client.

Base URL: https://alphafold.ebi.ac.uk/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "AlphaFold"
BASE_URL = "https://alphafold.ebi.ac.uk/api/"


async def predict(
    server: BaseLifeSciencesServer,
    sequence: str,
) -> dict[str, Any]:
    """Submit a protein sequence for AlphaFold structure prediction."""
    url = f"{BASE_URL}prediction/submit"
    payload = {"sequence": sequence}
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=sequence[:20])
    return response.json()


async def status(
    server: BaseLifeSciencesServer,
    job_id: str,
) -> dict[str, Any]:
    """Get the status of an AlphaFold prediction job."""
    url = f"{BASE_URL}prediction/{job_id}"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=job_id)
    return response.json()
