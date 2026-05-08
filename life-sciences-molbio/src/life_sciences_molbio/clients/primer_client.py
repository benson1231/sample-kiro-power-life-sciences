"""Primer3 and Primer-BLAST API client.

Primer3 API: https://primer3.ut.ee/
Primer-BLAST: https://www.ncbi.nlm.nih.gov/tools/primer-blast/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Primer3"
PRIMER3_BASE_URL = "https://primer3.ut.ee/"
PRIMER_BLAST_URL = "https://www.ncbi.nlm.nih.gov/tools/primer-blast/primertool.cgi"


async def design(
    server: BaseLifeSciencesServer,
    sequence: str,
    product_size_min: int = 100,
    product_size_max: int = 300,
) -> dict[str, Any]:
    """Design PCR primers using Primer3."""
    url = f"{PRIMER3_BASE_URL}cgi-bin/primer3/primer3web_results.cgi"
    data = {
        "SEQUENCE_TEMPLATE": sequence,
        "PRIMER_PRODUCT_SIZE_RANGE": f"{product_size_min}-{product_size_max}",
        "PRIMER_NUM_RETURN": "5",
        "Pick Primers": "Pick Primers",
    }
    response = await server._request_with_retry(
        "POST", url, data=data,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=sequence[:50])
    return {"status": "completed", "raw_output": response.text[:5000]}


async def blast(
    server: BaseLifeSciencesServer,
    forward: str,
    reverse: str,
    organism: str = "Homo sapiens",
) -> dict[str, Any]:
    """Check primer specificity using Primer-BLAST."""
    data = {
        "PRIMER5_START": "",
        "PRIMER5_END": "",
        "PRIMER3_START": "",
        "PRIMER3_END": "",
        "INPUT_PRIMER_LEFT": forward,
        "INPUT_PRIMER_RIGHT": reverse,
        "ORGANISM": organism,
        "CMD": "request",
    }
    response = await server._request_with_retry(
        "POST", PRIMER_BLAST_URL, data=data,
    )
    await server._handle_api_error(response, "Primer-BLAST")
    return {"status": "submitted", "raw_output": response.text[:5000]}
