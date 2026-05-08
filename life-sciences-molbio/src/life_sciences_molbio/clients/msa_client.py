"""EBI Multiple Sequence Alignment API client.

Base URL: https://www.ebi.ac.uk/Tools/services/rest/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "EBI MSA"
BASE_URL = "https://www.ebi.ac.uk/Tools/services/rest/"

_JSON_HEADERS = {"Accept": "application/json"}


async def align(
    server: BaseLifeSciencesServer,
    sequences: list[str],
    tool: str = "clustalo",
) -> dict[str, Any]:
    """Submit a multiple sequence alignment job."""
    url = f"{BASE_URL}{tool}/run"
    # Build FASTA input from sequences
    fasta_input = ""
    for i, seq in enumerate(sequences):
        if not seq.startswith(">"):
            fasta_input += f">seq{i + 1}\n"
        fasta_input += seq + "\n"
    data = {
        "email": "kiro-life-sciences@example.com",
        "sequence": fasta_input,
        "outfmt": "clustal_num",
    }
    response = await server._request_with_retry(
        "POST", url, data=data,
    )
    await server._handle_api_error(response, SERVICE_NAME)
    job_id = response.text.strip()
    return {"job_id": job_id, "tool": tool, "status": "submitted"}
