"""Unit tests for life-sciences-microbiology MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-microbiology")
    yield srv
    await srv.cleanup()


class TestSILVASearch:
    @respx.mock
    async def test_silva_search(self, server: BaseLifeSciencesServer):
        from life_sciences_microbiology.clients import silva_client

        respx.get("https://www.arb-silva.de/api/search").respond(
            200, json={"results": [{"accession": "AB001"}], "count": 1},
        )
        result = await silva_client.search(server, "Lactobacillus")
        assert result["count"] == 1


class TestGreengenesSearch:
    @respx.mock
    async def test_greengenes_search(self, server: BaseLifeSciencesServer):
        from life_sciences_microbiology.clients import greengenes_client

        respx.get("https://greengenes.secondgenome.com/api/search").respond(
            200, json={"results": [{"otu_id": "4470135"}]},
        )
        result = await greengenes_client.search(server, "Firmicutes")
        assert "results" in result


class TestMGRASTSearch:
    @respx.mock
    async def test_mgrast_search(self, server: BaseLifeSciencesServer):
        from life_sciences_microbiology.clients import mgrast_client

        respx.get("https://api.mg-rast.org/search").respond(
            200, json={"data": [{"id": "mgm4440613.3"}], "total_count": 1},
        )
        result = await mgrast_client.search(server, "soil metagenome")
        assert result["total_count"] == 1


class TestBVBRCSearch:
    @respx.mock
    async def test_bvbrc_search(self, server: BaseLifeSciencesServer):
        from life_sciences_microbiology.clients import bvbrc_client

        respx.get("https://www.bv-brc.org/api/genome/").respond(
            200, json=[{"genome_id": "83332.12", "genome_name": "M. tuberculosis"}],
        )
        result = await bvbrc_client.search(server, "tuberculosis")
        assert isinstance(result, list)


class TestBVBRCFeatures:
    @respx.mock
    async def test_bvbrc_features(self, server: BaseLifeSciencesServer):
        from life_sciences_microbiology.clients import bvbrc_client

        respx.get("https://www.bv-brc.org/api/genome_feature/").respond(
            200, json=[{"feature_id": "fig|83332.12.peg.1"}],
        )
        result = await bvbrc_client.features(server, "83332.12")
        assert isinstance(result, list)


class TestCARDSearch:
    @respx.mock
    async def test_card_search(self, server: BaseLifeSciencesServer):
        from life_sciences_microbiology.clients import card_client

        respx.get("https://card.mcmaster.ca/api/search").respond(
            200, json={"results": [{"aro_name": "mecA"}], "count": 1},
        )
        result = await card_client.search(server, "mecA")
        assert result["count"] == 1


class TestCARDAnalyze:
    @respx.mock
    async def test_card_analyze(self, server: BaseLifeSciencesServer):
        from life_sciences_microbiology.clients import card_client

        respx.post("https://card.mcmaster.ca/api/blast").respond(
            200, json={"hits": [{"aro_name": "mecA", "identity": 99.5}]},
        )
        result = await card_client.analyze(server, "ATGCGATCGATCG")
        assert "hits" in result
