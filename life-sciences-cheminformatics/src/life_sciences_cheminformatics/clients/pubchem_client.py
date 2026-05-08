"""PubChem PUG REST API client.

Base URL: https://pubchem.ncbi.nlm.nih.gov/rest/pug/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "PubChem"
BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/"

_JSON_HEADERS = {"Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search PubChem compounds by name or SMILES."""
    url = f"{BASE_URL}compound/name/{query}/cids/JSON"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    data = response.json()
    cids = data.get("IdentifierList", {}).get("CID", [])[:max_results]
    return {"query": query, "cids": cids, "count": len(cids)}


async def properties(
    server: BaseLifeSciencesServer,
    cid: str,
) -> dict[str, Any]:
    """Get compound properties by CID."""
    url = (
        f"{BASE_URL}compound/cid/{cid}/property/"
        "MolecularFormula,MolecularWeight,IUPACName,XLogP,"
        "ExactMass,TPSA,HBondDonorCount,HBondAcceptorCount,"
        "RotatableBondCount,Complexity/JSON"
    )
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=cid)
    return response.json()
