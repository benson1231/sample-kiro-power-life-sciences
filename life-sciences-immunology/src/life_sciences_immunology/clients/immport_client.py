"""ImmPort API client.

Base URL: https://api.immport.org/
Requires IMMPORT_USERNAME and IMMPORT_PASSWORD environment variables.
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import AuthenticationError, BaseLifeSciencesServer

SERVICE_NAME = "ImmPort"
BASE_URL = "https://api.immport.org/"
OBTAIN_URL = "https://www.immport.org/registration"


def _get_credentials() -> tuple[str, str]:
    """Return ImmPort credentials or raise AuthenticationError."""
    username = os.environ.get("IMMPORT_USERNAME")
    password = os.environ.get("IMMPORT_PASSWORD")
    if not username or not password:
        raise AuthenticationError(
            service=SERVICE_NAME,
            obtain_url=OBTAIN_URL,
            message=(
                "IMMPORT_USERNAME and IMMPORT_PASSWORD environment variables must be set. "
                f"Register at {OBTAIN_URL}"
            ),
        )
    return username, password


async def _get_token(server: BaseLifeSciencesServer) -> str:
    """Authenticate and return an access token."""
    username, password = _get_credentials()
    url = f"{BASE_URL}auth/token"
    data = {"username": username, "password": password}
    response = await server._request_with_retry(
        "POST", url, data=data,
    )
    await server._handle_api_error(
        response, SERVICE_NAME, obtain_url=OBTAIN_URL,
    )
    return response.json().get("token", "")


async def search(
    server: BaseLifeSciencesServer,
    keyword: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search ImmPort studies by keyword."""
    token = await _get_token(server)
    url = f"{BASE_URL}data/query/result/study"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    params = {"term": keyword, "pageSize": max_results}
    response = await server._request_with_retry(
        "GET", url, headers=headers, params=params,
    )
    await server._handle_api_error(
        response, SERVICE_NAME, query=keyword, obtain_url=OBTAIN_URL,
    )
    return response.json()
