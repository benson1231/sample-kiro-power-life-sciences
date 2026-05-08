"""HMMER API client.

Base URL: https://www.ebi.ac.uk/Tools/hmmer/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "HMMER"
BASE_URL = "https://www.ebi.ac.uk/Tools/hmmer/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    sequence: str,
    database: str = "pfam",
) -> dict[str, Any]:
    """Search protein sequence against HMMER database."""
    url = f"{BASE_URL}search/hmmscan"
    data = {
        "seqdb": database,
        "seq": sequence,
    }
    headers = {**_JSON_HEADERS, "Content-Type": "application/x-www-form-urlencoded"}
    response = await server._request_with_retry(
        "POST", url, data=data, headers=headers,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=sequence[:50])
    return response.json()
