"""LIMS (Laboratory Information Management System) client.

Provides SiLA 2 compatible sample management interface.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "LIMS"
BASE_URL = "https://lims.example.org/api/v1/"


async def get_sample(
    server: BaseLifeSciencesServer,
    sample_id: str,
) -> dict[str, Any]:
    """Get sample information by ID from LIMS."""
    url = f"{BASE_URL}samples/{sample_id}"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=sample_id)
    return response.json()


async def create_sample(
    server: BaseLifeSciencesServer,
    sample_type: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """Create a new sample in LIMS."""
    url = f"{BASE_URL}samples"
    payload = {"sample_type": sample_type, "metadata": metadata}
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=sample_type)
    return response.json()
