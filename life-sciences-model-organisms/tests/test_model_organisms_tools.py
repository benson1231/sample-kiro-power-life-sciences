"""Unit tests for life-sciences-model-organisms MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-model-organisms")
    yield srv
    await srv.cleanup()


class TestFlyBaseGene:
    @respx.mock
    async def test_flybase_gene(self, server: BaseLifeSciencesServer):
        from life_sciences_model_organisms.clients import flybase_client

        respx.get("https://api.flybase.org/api/v1.0/gene/dpp").respond(
            200, json={"gene": "dpp", "species": "Drosophila melanogaster"},
        )
        result = await flybase_client.gene(server, "dpp")
        assert result["gene"] == "dpp"


class TestWormBaseGene:
    @respx.mock
    async def test_wormbase_gene(self, server: BaseLifeSciencesServer):
        from life_sciences_model_organisms.clients import wormbase_client

        respx.get("https://wormbase.org/rest/field/gene/unc-13/overview").respond(
            200, json={"class": "gene", "name": "unc-13"},
        )
        result = await wormbase_client.gene(server, "unc-13")
        assert result["name"] == "unc-13"


class TestZFINGene:
    @respx.mock
    async def test_zfin_gene(self, server: BaseLifeSciencesServer):
        from life_sciences_model_organisms.clients import zfin_client

        respx.get("https://zfin.org/action/api/search").respond(
            200, json={"results": [{"name": "shha"}], "total": 1},
        )
        result = await zfin_client.gene(server, "shha")
        assert result["total"] == 1


class TestMGIGene:
    @respx.mock
    async def test_mgi_gene(self, server: BaseLifeSciencesServer):
        from life_sciences_model_organisms.clients import mgi_client

        respx.get("https://www.informatics.jax.org/api/marker/Pax6").respond(
            200, json={"symbol": "Pax6", "organism": "mouse"},
        )
        result = await mgi_client.gene(server, "Pax6")
        assert result["symbol"] == "Pax6"


class TestSGDGene:
    @respx.mock
    async def test_sgd_gene(self, server: BaseLifeSciencesServer):
        from life_sciences_model_organisms.clients import sgd_client

        respx.get("https://www.yeastgenome.org/backend/locus/ACT1").respond(
            200, json={"locus": "ACT1", "organism": "S. cerevisiae"},
        )
        result = await sgd_client.gene(server, "ACT1")
        assert result["locus"] == "ACT1"
