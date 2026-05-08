"""Unit tests for life-sciences-biobanking MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-biobanking")
    yield srv
    await srv.cleanup()


class TestBBMRISearch:
    @respx.mock
    async def test_bbmri_search(self, server: BaseLifeSciencesServer):
        from life_sciences_biobanking.clients import bbmri_client

        respx.get(
            "https://directory.bbmri-eric.eu/api/v2/eu_bbmri_eric_collections"
        ).respond(
            200, json={"items": [{"id": "bbmri-eric:ID:CZ_MMCI"}]},
        )
        result = await bbmri_client.search(server, disease="cancer")
        assert "items" in result


class TestBioSampleSearch:
    @respx.mock
    async def test_biosample_search(self, server: BaseLifeSciencesServer):
        from life_sciences_biobanking.clients import biosample_client

        respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").respond(
            200, json={"esearchresult": {"idlist": ["SAMN001"], "count": "1"}},
        )
        result = await biosample_client.search(server, "human blood")
        assert "esearchresult" in result


class TestLIMSSample:
    @respx.mock
    async def test_lims_get_sample(self, server: BaseLifeSciencesServer):
        from life_sciences_biobanking.clients import lims_client

        respx.get("https://lims.example.org/api/v1/samples/S001").respond(
            200, json={"sample_id": "S001", "type": "blood"},
        )
        result = await lims_client.get_sample(server, "S001")
        assert result["sample_id"] == "S001"


class TestProtocolsSearch:
    @respx.mock
    async def test_protocols_search(self, server: BaseLifeSciencesServer):
        from life_sciences_biobanking.clients import protocols_client

        respx.get("https://www.protocols.io/api/v4/protocols").respond(
            200, json={"items": [{"title": "DNA extraction protocol"}]},
        )
        result = await protocols_client.search(server, "DNA extraction")
        assert "items" in result
