"""Unit tests for life-sciences-cellbiology MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-cellbiology")
    yield srv
    await srv.cleanup()


class TestCellAtlasSearch:
    @respx.mock
    async def test_cell_atlas_search(self, server: BaseLifeSciencesServer):
        from life_sciences_cellbiology.clients import cell_atlas_client

        respx.get("https://service.azul.data.humancellatlas.org/index/projects").respond(
            200, json={"hits": [{"projectTitle": "HCA project"}]},
        )
        result = await cell_atlas_client.search(server, "CD4")
        assert "hits" in result


class TestCellxGeneDatasets:
    @respx.mock
    async def test_cellxgene_datasets(self, server: BaseLifeSciencesServer):
        from life_sciences_cellbiology.clients import cellxgene_client

        respx.get("https://api.cellxgene.cziscience.com/dp/v1/datasets/index").respond(
            200, json=[{"dataset_id": "ds1", "tissue": "lung"}],
        )
        result = await cellxgene_client.datasets(server, tissue="lung")
        assert isinstance(result, list)


class TestCellxGeneExpression:
    @respx.mock
    async def test_cellxgene_expression(self, server: BaseLifeSciencesServer):
        from life_sciences_cellbiology.clients import cellxgene_client

        respx.get(
            "https://api.cellxgene.cziscience.com/dp/v1/datasets/ds1/expression"
        ).respond(
            200, json={"gene": "CD4", "expression": [0.1, 0.5, 0.9]},
        )
        result = await cellxgene_client.expression(server, "ds1", "CD4")
        assert result["gene"] == "CD4"


class TestSCEASearch:
    @respx.mock
    async def test_scea_search(self, server: BaseLifeSciencesServer):
        from life_sciences_cellbiology.clients import scea_client

        respx.get("https://www.ebi.ac.uk/gxa/sc/json/search").respond(
            200, json={"results": [{"experimentAccession": "E-MTAB-1"}]},
        )
        result = await scea_client.search(server, "CD8A")
        assert "results" in result
