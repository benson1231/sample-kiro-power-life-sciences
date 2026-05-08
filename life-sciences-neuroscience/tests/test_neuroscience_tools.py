"""Unit tests for life-sciences-neuroscience MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-neuroscience")
    yield srv
    await srv.cleanup()


class TestAllenBrainSearch:
    @respx.mock
    async def test_allen_brain_search(self, server: BaseLifeSciencesServer):
        from life_sciences_neuroscience.clients import allen_brain_client

        respx.get("https://api.brain-map.org/api/v2/data/query.json").respond(
            200, json={"msg": [{"id": 1, "acronym": "BDNF"}], "success": True},
        )
        result = await allen_brain_client.search(server, "BDNF")
        assert result["success"] is True


class TestNeuroMorphoSearch:
    @respx.mock
    async def test_neuromorpho_search(self, server: BaseLifeSciencesServer):
        from life_sciences_neuroscience.clients import neuromorpho_client

        respx.get("https://neuromorpho.org/api/neuron/select").respond(
            200, json={"_embedded": {"neuronResources": [{"neuron_name": "n1"}]}},
        )
        result = await neuromorpho_client.search(server, "pyramidal")
        assert "_embedded" in result


class TestOpenNeuroSearch:
    @respx.mock
    async def test_openneuro_search(self, server: BaseLifeSciencesServer):
        from life_sciences_neuroscience.clients import openneuro_client

        respx.get("https://openneuro.org/crn/datasets").respond(
            200, json={"datasets": [{"id": "ds000001"}]},
        )
        result = await openneuro_client.search(server, "fMRI")
        assert "datasets" in result


class TestBrainMapSearch:
    @respx.mock
    async def test_brainmap_search(self, server: BaseLifeSciencesServer):
        from life_sciences_neuroscience.clients import brainmap_client

        respx.get("https://brainmap.org/api/search").respond(
            200, json={"results": [{"region": "hippocampus"}]},
        )
        result = await brainmap_client.search(server, "hippocampus")
        assert "results" in result
