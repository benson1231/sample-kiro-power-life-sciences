"""Pfam API client (via InterPro).

Pfam is now part of InterPro.
Base URL: https://www.ebi.ac.uk/interpro/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Pfam"
BASE_URL = "https://www.ebi.ac.uk/interpro/api/"


async def family(
    server: BaseLifeSciencesServer,
    family_id: str,
) -> dict[str, Any]:
    """Query Pfam by family identifier (e.g. ``PF00069``)."""
    url = f"{BASE_URL}entry/pfam/{family_id}"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=family_id)
    return response.json()
