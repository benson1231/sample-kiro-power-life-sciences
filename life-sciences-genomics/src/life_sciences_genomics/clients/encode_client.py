"""ENCODE API client.

Base URL: https://www.encodeproject.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ENCODE"
BASE_URL = "https://www.encodeproject.org/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    biosample: str = "",
    assay: str = "",
    target: str = "",
) -> dict[str, Any]:
    """Search ENCODE experiments by biosample, assay, and/or target."""
    url = f"{BASE_URL}search/"
    params: dict[str, Any] = {
        "type": "Experiment",
        "format": "json",
        "limit": 25,
    }
    if biosample:
        params["biosample_ontology.term_name"] = biosample
    if assay:
        params["assay_title"] = assay
    if target:
        params["target.label"] = target

    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME)
    return response.json()
