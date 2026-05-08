"""FHIR (Fast Healthcare Interoperability Resources) API client.

Base URL: https://hapi.fhir.org/baseR4/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "FHIR"
BASE_URL = "https://hapi.fhir.org/baseR4/"

_JSON_HEADERS = {"Accept": "application/fhir+json", "Content-Type": "application/fhir+json"}


async def search(
    server: BaseLifeSciencesServer,
    resource_type: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Search FHIR resources by type and parameters."""
    url = f"{BASE_URL}{resource_type}"
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=resource_type)
    return response.json()


async def create(
    server: BaseLifeSciencesServer,
    resource_type: str,
    resource: dict[str, Any],
) -> dict[str, Any]:
    """Create a FHIR resource."""
    url = f"{BASE_URL}{resource_type}"
    response = await server._request_with_retry(
        "POST", url, json=resource, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=resource_type)
    return response.json()
