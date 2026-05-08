"""SwissDock docking API client.

Base URL: https://www.swissdock.ch/api/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "SwissDock"
BASE_URL = "https://www.swissdock.ch/api/"


async def submit(
    server: BaseLifeSciencesServer,
    receptor_pdb: str,
    ligand_smiles: str,
) -> dict[str, Any]:
    """Submit a docking job to SwissDock."""
    url = f"{BASE_URL}docking"
    data = {
        "target": receptor_pdb,
        "ligand": ligand_smiles,
    }
    response = await server._request_with_retry(
        "POST", url, data=data,
    )
    await server._handle_api_error(response, SERVICE_NAME)
    return response.json()
