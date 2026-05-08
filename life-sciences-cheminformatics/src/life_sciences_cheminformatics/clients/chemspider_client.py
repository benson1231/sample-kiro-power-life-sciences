"""ChemSpider API client.

Base URL: https://api.rsc.org/compounds/v1/
Requires CHEMSPIDER_API_KEY environment variable.
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import AuthenticationError, BaseLifeSciencesServer

SERVICE_NAME = "ChemSpider"
BASE_URL = "https://api.rsc.org/compounds/v1/"
OBTAIN_URL = "https://developer.rsc.org/"


def _get_api_key() -> str:
    """Return the ChemSpider API key or raise AuthenticationError."""
    key = os.environ.get("CHEMSPIDER_API_KEY")
    if not key:
        raise AuthenticationError(
            service=SERVICE_NAME,
            obtain_url=OBTAIN_URL,
            message=(
                "CHEMSPIDER_API_KEY environment variable is not set. "
                f"Obtain a key at {OBTAIN_URL}"
            ),
        )
    return key


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search ChemSpider compounds by name or formula."""
    api_key = _get_api_key()
    url = f"{BASE_URL}filter/name"
    headers = {"apikey": api_key, "Content-Type": "application/json"}
    payload = {"name": query}
    response = await server._request_with_retry(
        "POST", url, headers=headers, json=payload,
    )
    await server._handle_api_error(
        response, SERVICE_NAME, query=query, obtain_url=OBTAIN_URL,
    )
    data = response.json()
    query_id = data.get("queryId", "")

    # Retrieve results
    results_url = f"{BASE_URL}filter/{query_id}/results"
    results_response = await server._request_with_retry(
        "GET", results_url, headers={"apikey": api_key},
    )
    await server._handle_api_error(
        results_response, SERVICE_NAME, query=query, obtain_url=OBTAIN_URL,
    )
    return results_response.json()
