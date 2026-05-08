"""Unit tests for life-sciences-agriculture MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-agriculture")
    yield srv
    await srv.cleanup()


class TestPhytozomeSearch:
    @respx.mock
    async def test_phytozome_search(self, server: BaseLifeSciencesServer):
        from life_sciences_agriculture.clients import phytozome_client

        respx.get("https://phytozome-next.jgi.doe.gov/api/search").respond(
            200, json={"results": [{"organism": "Arabidopsis thaliana"}]},
        )
        result = await phytozome_client.search(server, "Arabidopsis")
        assert "results" in result


class TestTAIRSearch:
    @respx.mock
    async def test_tair_search(self, server: BaseLifeSciencesServer):
        from life_sciences_agriculture.clients import tair_client

        respx.get("https://www.arabidopsis.org/api/search").respond(
            200, json={"results": [{"locus": "AT1G01010"}]},
        )
        result = await tair_client.search(server, "AT1G01010")
        assert "results" in result


class TestGrameneSearch:
    @respx.mock
    async def test_gramene_search(self, server: BaseLifeSciencesServer):
        from life_sciences_agriculture.clients import gramene_client

        respx.get("https://data.gramene.org/search").respond(
            200, json={"results": [{"species": "Oryza sativa"}]},
        )
        result = await gramene_client.search(server, "rice")
        assert "results" in result


class TestPlantGDBSearch:
    @respx.mock
    async def test_plantgdb_search(self, server: BaseLifeSciencesServer):
        from life_sciences_agriculture.clients import plantgdb_client

        respx.get("http://www.plantgdb.org/api/search").respond(
            200, json={"results": [{"species": "Zea mays"}]},
        )
        result = await plantgdb_client.search(server, "maize")
        assert "results" in result
