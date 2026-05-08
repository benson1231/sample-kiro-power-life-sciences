"""OMIM (Online Mendelian Inheritance in Man) API client.

Base URL: https://api.omim.org/api/
Requires OMIM_API_KEY environment variable.
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import AuthenticationError, BaseLifeSciencesServer

SERVICE_NAME = "OMIM"
BASE_URL = "https://api.omim.org/api"
OBTAIN_URL = "https://www.omim.org/api"

_JSON_HEADERS = {"Accept": "application/json"}


def _get_api_key() -> str:
    """Return the OMIM API key or raise AuthenticationError."""
    key = os.environ.get("OMIM_API_KEY")
    if not key:
        raise AuthenticationError(
            service=SERVICE_NAME,
            obtain_url=OBTAIN_URL,
            message=(
                "OMIM_API_KEY environment variable is not set. "
                f"Obtain a key at {OBTAIN_URL}"
            ),
        )
    return key


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search OMIM entries by keyword."""
    api_key = _get_api_key()
    url = f"{BASE_URL}/entry/search"
    params = {
        "search": query,
        "limit": max_results,
        "format": "json",
        "apiKey": api_key,
    }
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(
        response, SERVICE_NAME, query=query, obtain_url=OBTAIN_URL,
    )
    return response.json()


async def entry(
    server: BaseLifeSciencesServer,
    mim_number: str,
) -> dict[str, Any]:
    """Get OMIM entry by MIM number."""
    api_key = _get_api_key()
    url = f"{BASE_URL}/entry"
    params = {
        "mimNumber": mim_number,
        "format": "json",
        "apiKey": api_key,
        "include": "all",
    }
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(
        response, SERVICE_NAME, query=mim_number, obtain_url=OBTAIN_URL,
    )
    return response.json()
