"""NCBI BLAST API client.

Base URL: https://blast.ncbi.nlm.nih.gov/Blast.cgi
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "NCBI BLAST"
BASE_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"


async def search(
    server: BaseLifeSciencesServer,
    sequence: str,
    database: str = "nr",
    program: str = "blastn",
) -> dict[str, Any]:
    """Submit a BLAST search and return the request ID (RID)."""
    params = {
        "CMD": "Put",
        "PROGRAM": program,
        "DATABASE": database,
        "QUERY": sequence,
        "FORMAT_TYPE": "JSON2",
    }
    response = await server._request_with_retry(
        "POST", BASE_URL, data=params,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=sequence[:50])
    text = response.text
    # Parse RID from BLAST response
    rid = ""
    for line in text.splitlines():
        if line.strip().startswith("RID ="):
            rid = line.split("=")[1].strip()
            break
    return {"rid": rid, "status": "submitted", "program": program, "database": database}


async def results(
    server: BaseLifeSciencesServer,
    rid: str,
) -> dict[str, Any]:
    """Get BLAST results by request ID."""
    params = {
        "CMD": "Get",
        "RID": rid,
        "FORMAT_TYPE": "JSON2",
    }
    response = await server._request_with_retry(
        "GET", BASE_URL, params=params,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=rid)
    # Check if results are ready
    text = response.text
    if "Status=WAITING" in text:
        return {"rid": rid, "status": "waiting", "message": "Results not yet ready. Try again later."}
    if "Status=FAILED" in text:
        return {"rid": rid, "status": "failed", "message": "BLAST search failed."}
    if "Status=UNKNOWN" in text:
        return {"rid": rid, "status": "unknown", "message": "RID not found or expired."}
    try:
        return response.json()
    except Exception:
        return {"rid": rid, "status": "ready", "raw": text[:5000]}
