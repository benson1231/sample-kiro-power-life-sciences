"""BBMRI (Biobanking and BioMolecular Resources Research Infrastructure) API client.

Base URL: https://directory.bbmri-eric.eu/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BBMRI"
BASE_URL = "https://directory.bbmri-eric.eu/api/"


async def search(
    server: BaseLifeSciencesServer,
    disease: str = "",
    material: str = "",
    country: str = "",
) -> dict[str, Any]:
    """Search BBMRI biobank collections by disease, material type, and/or country."""
    url = f"{BASE_URL}v2/eu_bbmri_eric_collections"
    params: dict[str, Any] = {}
    filters = []
    if disease:
        filters.append(f"diagnosis_available=={disease}")
    if material:
        filters.append(f"materials=={material}")
    if country:
        filters.append(f"country=={country}")
    if filters:
        params["q"] = ";".join(filters)
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=disease or material or country)
    return response.json()
