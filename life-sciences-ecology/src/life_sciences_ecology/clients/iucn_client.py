"""IUCN Red List API client.

Base URL: https://apiv3.iucnredlist.org/api/v3/
Requires IUCN_API_KEY environment variable.
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import AuthenticationError, BaseLifeSciencesServer

SERVICE_NAME = "IUCN Red List"
BASE_URL = "https://apiv3.iucnredlist.org/api/v3/"
OBTAIN_URL = "https://apiv3.iucnredlist.org/api/v3/token"


def _get_api_key() -> str:
    """Return the IUCN API key or raise AuthenticationError."""
    key = os.environ.get("IUCN_API_KEY")
    if not key:
        raise AuthenticationError(
            service=SERVICE_NAME,
            obtain_url=OBTAIN_URL,
            message=(
                "IUCN_API_KEY environment variable is not set. "
                f"Obtain a key at {OBTAIN_URL}"
            ),
        )
    return key


async def species(
    server: BaseLifeSciencesServer,
    species: str,
) -> dict[str, Any]:
    """Get IUCN Red List status for a species."""
    api_key = _get_api_key()
    url = f"{BASE_URL}species/{species}"
    params: dict[str, Any] = {"token": api_key}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(
        response, SERVICE_NAME, query=species, obtain_url=OBTAIN_URL,
    )
    return response.json()
