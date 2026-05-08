"""gnomAD API client.

Base URL: https://gnomad.broadinstitute.org/api/
Uses the gnomAD GraphQL API for variant queries.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "gnomAD"
BASE_URL = "https://gnomad.broadinstitute.org/api/"

_VARIANT_QUERY = """
query GnomadVariant($variantId: String!) {
  variant(variantId: $variantId, dataset: gnomad_r4) {
    variant_id
    chrom
    pos
    ref
    alt
    exome {
      ac
      an
      af
    }
    genome {
      ac
      an
      af
    }
  }
}
"""


async def variant(
    server: BaseLifeSciencesServer,
    variant_id: str,
) -> dict[str, Any]:
    """Get allele frequency data for a variant (e.g. '1-55516888-G-A')."""
    payload = {
        "query": _VARIANT_QUERY,
        "variables": {"variantId": variant_id},
    }
    response = await server._request_with_retry(
        "POST", BASE_URL, json=payload,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=variant_id)
    return response.json()
