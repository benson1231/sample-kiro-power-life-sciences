"""Unit tests for life-sciences-epigenomics MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-epigenomics")
    yield srv
    await srv.cleanup()


class TestIHECSearch:
    @respx.mock
    async def test_ihec_search(self, server: BaseLifeSciencesServer):
        from life_sciences_epigenomics.clients import ihec_client

        respx.get("https://epigenomesportal.ca/ihec/api/v2/datasets.json").respond(
            200, json={"datasets": [{"id": "IHECRE00000001"}]},
        )
        result = await ihec_client.search(server, "liver")
        assert "datasets" in result


class TestRoadmapSearch:
    @respx.mock
    async def test_roadmap_search(self, server: BaseLifeSciencesServer):
        from life_sciences_epigenomics.clients import roadmap_client

        respx.get("https://egg2.wustl.edu/roadmap/data/byFileType/metadata.json").respond(
            200, json={"samples": [{"eid": "E003", "tissue": "brain"}]},
        )
        result = await roadmap_client.search(server, "brain")
        assert "samples" in result


class TestMethBaseSearch:
    @respx.mock
    async def test_methbase_search(self, server: BaseLifeSciencesServer):
        from life_sciences_epigenomics.clients import methbase_client

        respx.get("http://smithlabresearch.org/methbase/api/methylomes").respond(
            200, json={"methylomes": [{"species": "human", "tissue": "brain"}]},
        )
        result = await methbase_client.search(server, "human")
        assert "methylomes" in result
