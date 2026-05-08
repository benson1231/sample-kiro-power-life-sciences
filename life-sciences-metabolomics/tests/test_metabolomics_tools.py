"""Unit tests for life-sciences-metabolomics MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-metabolomics")
    yield srv
    await srv.cleanup()


class TestHMDBSearch:
    @respx.mock
    async def test_hmdb_search(self, server: BaseLifeSciencesServer):
        from life_sciences_metabolomics.clients import hmdb_client

        respx.get("https://hmdb.ca/api/v1/metabolites/search").respond(
            200, json={"results": [{"hmdb_id": "HMDB0000001", "name": "1-Methylhistidine"}]},
        )
        result = await hmdb_client.search(server, "glucose")
        assert "results" in result


class TestMetaboLightsSearch:
    @respx.mock
    async def test_metabolights_search(self, server: BaseLifeSciencesServer):
        from life_sciences_metabolomics.clients import metabolights_client

        respx.get("https://www.ebi.ac.uk/metabolights/ws/studies/search").respond(
            200, json={"studies": [{"accession": "MTBLS1"}]},
        )
        result = await metabolights_client.search(server, "diabetes")
        assert "studies" in result


class TestMETLINSearch:
    @respx.mock
    async def test_metlin_search(self, server: BaseLifeSciencesServer):
        from life_sciences_metabolomics.clients import metlin_client

        respx.get("https://metlin.scripps.edu/api/search").respond(
            200, json={"results": [{"name": "Glucose", "mass": 180.063}]},
        )
        result = await metlin_client.search(server, 180.063)
        assert "results" in result


class TestMassBankSearch:
    @respx.mock
    async def test_massbank_search(self, server: BaseLifeSciencesServer):
        from life_sciences_metabolomics.clients import massbank_client

        respx.get("https://massbank.eu/MassBank/api/records/search").respond(
            200, json={"records": [{"accession": "PR100001"}]},
        )
        result = await massbank_client.search(server, "caffeine")
        assert "records" in result
