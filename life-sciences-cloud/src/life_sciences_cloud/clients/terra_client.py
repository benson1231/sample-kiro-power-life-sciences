"""Terra (Broad Institute) API client.

Base URL: https://api.firecloud.org/api/
Requires TERRA_TOKEN environment variable (OAuth token).
"""

from __future__ import annotations

import os
from typing import Any

from life_sciences_common import AuthenticationError, BaseLifeSciencesServer

SERVICE_NAME = "Terra"
BASE_URL = "https://api.firecloud.org/api/"
OBTAIN_URL = "https://app.terra.bio/"


def _get_token() -> str:
    """Return the Terra OAuth token or raise AuthenticationError."""
    token = os.environ.get("TERRA_TOKEN")
    if not token:
        raise AuthenticationError(
            service=SERVICE_NAME,
            obtain_url=OBTAIN_URL,
            message=(
                "TERRA_TOKEN environment variable is not set. "
                f"Obtain a token at {OBTAIN_URL}"
            ),
        )
    return token


def _auth_headers() -> dict[str, str]:
    """Return authorization headers."""
    return {"Authorization": f"Bearer {_get_token()}"}


async def workspaces(
    server: BaseLifeSciencesServer,
) -> dict[str, Any]:
    """List Terra workspaces."""
    url = f"{BASE_URL}workspaces"
    response = await server._request_with_retry(
        "GET", url, headers=_auth_headers(),
    )
    await server._handle_api_error(
        response, SERVICE_NAME, obtain_url=OBTAIN_URL,
    )
    return response.json()


async def submit(
    server: BaseLifeSciencesServer,
    workspace: str,
    method: str,
    entity_set: str,
) -> dict[str, Any]:
    """Submit a workflow to a Terra workspace."""
    parts = workspace.split("/", 1)
    namespace = parts[0] if len(parts) > 1 else ""
    name = parts[1] if len(parts) > 1 else workspace
    url = f"{BASE_URL}workspaces/{namespace}/{name}/submissions"
    payload = {
        "methodConfigurationNamespace": namespace,
        "methodConfigurationName": method,
        "entityType": entity_set,
        "useCallCache": True,
    }
    response = await server._request_with_retry(
        "POST", url, json=payload, headers=_auth_headers(),
    )
    await server._handle_api_error(
        response, SERVICE_NAME, query=workspace, obtain_url=OBTAIN_URL,
    )
    return response.json()
