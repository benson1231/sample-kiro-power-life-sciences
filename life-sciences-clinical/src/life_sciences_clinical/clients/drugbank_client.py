"""DrugBank API client.

Base URL: https://go.drugbank.com/api/v1/
Requires DRUGBANK_API_KEY environment variable.
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import AuthenticationError, BaseLifeSciencesServer

SERVICE_NAME = "DrugBank"
BASE_URL = "https://go.drugbank.com/api/v1"
OBTAIN_URL = "https://go.drugbank.com/public_users/sign_up"

_JSON_HEADERS = {"Accept": "application/json"}


def _get_api_key() -> str:
    """Return the DrugBank API key or raise AuthenticationError."""
    key = os.environ.get("DRUGBANK_API_KEY")
    if not key:
        raise AuthenticationError(
            service=SERVICE_NAME,
            obtain_url=OBTAIN_URL,
            message=(
                "DRUGBANK_API_KEY environment variable is not set. "
                f"Obtain a key at {OBTAIN_URL}"
            ),
        )
    return key


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search DrugBank drugs by keyword."""
    api_key = _get_api_key()
    url = f"{BASE_URL}/drugs"
    headers = {**_JSON_HEADERS, "Authorization": f"Bearer {api_key}"}
    params = {"q": query, "per_page": max_results}
    response = await server._request_with_retry(
        "GET", url, headers=headers, params=params,
    )
    await server._handle_api_error(
        response, SERVICE_NAME, query=query, obtain_url=OBTAIN_URL,
    )
    return response.json()


async def drug(
    server: BaseLifeSciencesServer,
    drugbank_id: str,
) -> dict[str, Any]:
    """Get drug details by DrugBank ID (e.g. 'DB00945')."""
    api_key = _get_api_key()
    url = f"{BASE_URL}/drugs/{drugbank_id}"
    headers = {**_JSON_HEADERS, "Authorization": f"Bearer {api_key}"}
    response = await server._request_with_retry(
        "GET", url, headers=headers,
    )
    await server._handle_api_error(
        response, SERVICE_NAME, query=drugbank_id, obtain_url=OBTAIN_URL,
    )
    return response.json()
