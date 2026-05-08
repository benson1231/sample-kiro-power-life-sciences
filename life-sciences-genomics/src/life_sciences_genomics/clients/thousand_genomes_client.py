"""1000 Genomes API client (via Ensembl REST).

Base URL: https://rest.ensembl.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "1000 Genomes"
BASE_URL = "https://rest.ensembl.org/"

_JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


async def frequency(
    server: BaseLifeSciencesServer,
    variant: str,
    species: str = "homo_sapiens",
) -> dict[str, Any]:
    """Get population allele frequencies for a variant.

    Parameters
    ----------
    variant:
        Variant identifier, e.g. 'rs56116432' or '9:22125503-22125502:1/C'.
    species:
        Species name (default: homo_sapiens).
    """
    url = f"{BASE_URL}variation/{species}/{variant}"
    params = {"pops": "1", "content-type": "application/json"}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=variant)
    return response.json()
