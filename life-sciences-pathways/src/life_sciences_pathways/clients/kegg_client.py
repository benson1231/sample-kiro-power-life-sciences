"""KEGG (Kyoto Encyclopedia of Genes and Genomes) API client.

Base URL: https://rest.kegg.jp/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "KEGG"
BASE_URL = "https://rest.kegg.jp"


async def pathway(
    server: BaseLifeSciencesServer,
    pathway_id: str,
) -> dict[str, Any]:
    """Get KEGG pathway by pathway ID (e.g. 'hsa04110')."""
    url = f"{BASE_URL}/get/{pathway_id}"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=pathway_id)
    return {"pathway_id": pathway_id, "data": response.text}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
) -> dict[str, Any]:
    """Search KEGG pathways by keyword."""
    url = f"{BASE_URL}/find/pathway/{query}"
    response = await server._request_with_retry("GET", url)
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    # Parse tab-separated results
    results = []
    for line in response.text.strip().split("\n"):
        if line:
            parts = line.split("\t", 1)
            entry = {"id": parts[0]}
            if len(parts) > 1:
                entry["description"] = parts[1]
            results.append(entry)
    return {"query": query, "results": results}
