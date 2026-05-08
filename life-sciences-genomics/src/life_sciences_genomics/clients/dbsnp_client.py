"""dbSNP API client.

Base URL: https://api.ncbi.nlm.nih.gov/variation/v0/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "dbSNP"
BASE_URL = "https://api.ncbi.nlm.nih.gov/variation/v0/"


async def lookup(
    server: BaseLifeSciencesServer,
    rsid: str,
) -> dict[str, Any]:
    """Lookup a variant by rsID (e.g. 'rs328')."""
    # Strip leading 'rs' if present for the numeric ID
    numeric_id = rsid.lstrip("rs")
    url = f"{BASE_URL}refsnp/{numeric_id}"
    response = await server._request_with_retry(
        "GET", url, headers={"Accept": "application/json"},
    )
    await server._handle_api_error(response, SERVICE_NAME, query=rsid)
    return response.json()
