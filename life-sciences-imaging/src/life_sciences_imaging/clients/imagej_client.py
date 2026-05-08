"""ImageJ macro execution client.

Provides interface for running ImageJ macros on images.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ImageJ"
BASE_URL = "https://imagej.net/api/v1/"


async def macro(
    server: BaseLifeSciencesServer,
    macro: str,
    image: str,
) -> dict[str, Any]:
    """Run an ImageJ macro on an image."""
    url = f"{BASE_URL}macros/run"
    payload = {"macro": macro, "image": image}
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=macro)
    return response.json()
