"""CellxGene API client.

Base URL: https://api.cellxgene.cziscience.com/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "CellxGene"
BASE_URL = "https://api.cellxgene.cziscience.com/"


async def datasets(
    server: BaseLifeSciencesServer,
    tissue: str = "",
    cell_type: str = "",
) -> dict[str, Any]:
    """List CellxGene datasets, optionally filtered by tissue and/or cell type."""
    url = f"{BASE_URL}dp/v1/datasets/index"
    params: dict[str, Any] = {}
    if tissue:
        params["tissue"] = tissue
    if cell_type:
        params["cell_type"] = cell_type
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=tissue or cell_type)
    return response.json()


async def expression(
    server: BaseLifeSciencesServer,
    dataset_id: str,
    gene: str,
) -> dict[str, Any]:
    """Get gene expression data from a CellxGene dataset."""
    url = f"{BASE_URL}dp/v1/datasets/{dataset_id}/expression"
    params: dict[str, Any] = {"gene": gene}
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=gene)
    return response.json()
