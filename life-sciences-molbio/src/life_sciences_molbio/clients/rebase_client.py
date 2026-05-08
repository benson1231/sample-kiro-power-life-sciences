"""REBASE (Restriction Enzyme Database) API client.

Base URL: https://rebase.neb.com/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "REBASE"
BASE_URL = "https://rebase.neb.com/"

_JSON_HEADERS = {"Accept": "application/json"}


async def enzyme(
    server: BaseLifeSciencesServer,
    enzyme_name: str,
) -> dict[str, Any]:
    """Lookup restriction enzyme information from REBASE."""
    url = f"{BASE_URL}rebase/enz/{enzyme_name}.html"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=enzyme_name)
    # REBASE returns HTML; extract key info
    text = response.text
    return {
        "enzyme": enzyme_name,
        "source": "REBASE",
        "url": url,
        "raw_content": text[:3000],
    }
