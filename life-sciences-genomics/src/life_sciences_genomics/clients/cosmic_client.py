"""COSMIC API client.

Base URL: https://cancer.sanger.ac.uk/cosmic/api/
Requires COSMIC_API_KEY environment variable.
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import AuthenticationError, BaseLifeSciencesServer

SERVICE_NAME = "COSMIC"
BASE_URL = "https://cancer.sanger.ac.uk/cosmic/api/"
OBTAIN_URL = "https://cancer.sanger.ac.uk/cosmic/register"


def _get_api_key() -> str:
    """Return the COSMIC API key or raise AuthenticationError."""
    key = os.environ.get("COSMIC_API_KEY")
    if not key:
        raise AuthenticationError(
            service=SERVICE_NAME,
            obtain_url=OBTAIN_URL,
            message=(
                "COSMIC_API_KEY environment variable is not set. "
                f"Obtain a key at {OBTAIN_URL}"
            ),
        )
    return key


async def search(
    server: BaseLifeSciencesServer,
    gene: str,
) -> dict[str, Any]:
    """Search COSMIC mutations by gene name."""
    api_key = _get_api_key()
    url = f"{BASE_URL}v1/mutations"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"gene": gene}
    response = await server._request_with_retry(
        "GET", url, headers=headers, params=params,
    )
    await server._handle_api_error(
        response, SERVICE_NAME, query=gene, obtain_url=OBTAIN_URL,
    )
    return response.json()
