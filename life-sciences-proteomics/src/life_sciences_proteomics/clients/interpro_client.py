"""InterPro REST API client.

Base URL: https://www.ebi.ac.uk/interpro/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "InterPro"
BASE_URL = "https://www.ebi.ac.uk/interpro/api/"


async def lookup(
    server: BaseLifeSciencesServer,
    accession: str,
) -> dict[str, Any]:
    """Query InterPro by protein accession or domain ID.

    If *accession* starts with ``IPR`` it is treated as an InterPro entry
    identifier; otherwise it is treated as a protein accession and the
    protein endpoint is queried.
    """
    if accession.upper().startswith("IPR"):
        url = f"{BASE_URL}entry/interpro/{accession}"
    else:
        url = f"{BASE_URL}protein/uniprot/{accession}"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=accession)
    return response.json()
