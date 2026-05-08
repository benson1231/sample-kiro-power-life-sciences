"""REDCap API client.

Requires REDCAP_API_TOKEN environment variable.
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import AuthenticationError, BaseLifeSciencesServer

SERVICE_NAME = "REDCap"
BASE_URL = "https://redcap.example.org/api/"
OBTAIN_URL = "https://www.project-redcap.org/"


def _get_api_token() -> str:
    """Return the REDCap API token or raise AuthenticationError."""
    token = os.environ.get("REDCAP_API_TOKEN")
    if not token:
        raise AuthenticationError(
            service=SERVICE_NAME,
            obtain_url=OBTAIN_URL,
            message=(
                "REDCAP_API_TOKEN environment variable is not set. "
                f"Obtain a token at {OBTAIN_URL}"
            ),
        )
    return token


async def records(
    server: BaseLifeSciencesServer,
    project_id: str,
    filter: str = "",
) -> dict[str, Any]:
    """Get REDCap records for a project."""
    token = _get_api_token()
    payload: dict[str, Any] = {
        "token": token,
        "content": "record",
        "format": "json",
        "returnFormat": "json",
    }
    if filter:
        payload["filterLogic"] = filter
    response = await server._request_with_retry("POST", BASE_URL, data=payload)
    await server._handle_api_error(
        response, SERVICE_NAME, query=project_id, obtain_url=OBTAIN_URL,
    )
    return response.json()


async def export(
    server: BaseLifeSciencesServer,
    project_id: str,
    format: str = "json",
) -> dict[str, Any]:
    """Export REDCap project data."""
    token = _get_api_token()
    payload: dict[str, Any] = {
        "token": token,
        "content": "record",
        "format": format,
        "returnFormat": "json",
    }
    response = await server._request_with_retry("POST", BASE_URL, data=payload)
    await server._handle_api_error(
        response, SERVICE_NAME, query=project_id, obtain_url=OBTAIN_URL,
    )
    return response.json()
