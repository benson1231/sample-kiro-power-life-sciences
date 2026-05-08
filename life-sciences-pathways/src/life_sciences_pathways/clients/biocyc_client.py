"""BioCyc Pathway/Genome Database API client.

Base URL: https://websvc.biocyc.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BioCyc"
BASE_URL = "https://websvc.biocyc.org"

_XML_HEADERS = {"Accept": "application/xml"}


async def pathway(
    server: BaseLifeSciencesServer,
    pathway_id: str,
    organism: str = "HUMAN",
) -> dict[str, Any]:
    """Get BioCyc pathway by pathway ID and organism."""
    url = f"{BASE_URL}/apixml"
    params = {"fn": "pathways", "id": f"{organism}:{pathway_id}"}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_XML_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=pathway_id)
    return {
        "pathway_id": pathway_id,
        "organism": organism,
        "data": response.text,
    }
