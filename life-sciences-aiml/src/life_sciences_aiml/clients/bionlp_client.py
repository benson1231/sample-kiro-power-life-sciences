"""BioNLP (Biomedical Natural Language Processing) API client.

Base URL: https://bionlp.nlm.nih.gov/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BioNLP"
BASE_URL = "https://bionlp.nlm.nih.gov/api/"


async def entities(
    server: BaseLifeSciencesServer,
    text: str,
) -> dict[str, Any]:
    """Extract biomedical entities from text using BioNLP."""
    url = f"{BASE_URL}ner"
    payload = {"text": text}
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=text[:30])
    return response.json()


async def qa(
    server: BaseLifeSciencesServer,
    question: str,
    context: str,
) -> dict[str, Any]:
    """Answer a biomedical question given context using BioNLP."""
    url = f"{BASE_URL}qa"
    payload = {"question": question, "context": context}
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=question[:30])
    return response.json()
