"""Unit tests for life-sciences-ecology MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import AuthenticationError


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-ecology")
    yield srv
    await srv.cleanup()


class TestGBIFOccurrences:
    @respx.mock
    async def test_gbif_occurrences(self, server: BaseLifeSciencesServer):
        from life_sciences_ecology.clients import gbif_client

        respx.get("https://api.gbif.org/v1/occurrence/search").respond(
            200, json={"results": [{"species": "Panthera leo"}], "count": 1},
        )
        result = await gbif_client.occurrences(server, "Panthera leo")
        assert result["count"] == 1


class TestGBIFTaxonomy:
    @respx.mock
    async def test_gbif_taxonomy(self, server: BaseLifeSciencesServer):
        from life_sciences_ecology.clients import gbif_client

        respx.get("https://api.gbif.org/v1/species/match").respond(
            200, json={"usageKey": 5219404, "scientificName": "Panthera leo"},
        )
        result = await gbif_client.taxonomy(server, "Panthera leo")
        assert result["scientificName"] == "Panthera leo"


class TestBOLDSearch:
    @respx.mock
    async def test_bold_search(self, server: BaseLifeSciencesServer):
        from life_sciences_ecology.clients import bold_client

        respx.get("https://v3.boldsystems.org/index.php/API_Public/combined").respond(
            200, json={"bold_records": {"records": {"1": {"taxon": "Panthera leo"}}}},
        )
        result = await bold_client.search(server, "Panthera leo")
        assert "bold_records" in result


class TestINaturalistSearch:
    @respx.mock
    async def test_inaturalist_search(self, server: BaseLifeSciencesServer):
        from life_sciences_ecology.clients import inaturalist_client

        respx.get("https://api.inaturalist.org/v1/observations").respond(
            200, json={"results": [{"taxon": {"name": "Panthera leo"}}], "total_results": 1},
        )
        result = await inaturalist_client.search(server, "Panthera leo")
        assert result["total_results"] == 1


class TestIUCNSpecies:
    async def test_iucn_requires_auth(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_ecology.clients import iucn_client

        monkeypatch.delenv("IUCN_API_KEY", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            await iucn_client.species(server, "Panthera leo")
        assert "IUCN_API_KEY" in exc_info.value.message

    @respx.mock
    async def test_iucn_species_with_key(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_ecology.clients import iucn_client

        monkeypatch.setenv("IUCN_API_KEY", "test-key")
        respx.get("https://apiv3.iucnredlist.org/api/v3/species/Panthera leo").respond(
            200, json={"result": [{"category": "VU", "scientific_name": "Panthera leo"}]},
        )
        result = await iucn_client.species(server, "Panthera leo")
        assert result["result"][0]["category"] == "VU"


class TestMGnifySearch:
    @respx.mock
    async def test_mgnify_search(self, server: BaseLifeSciencesServer):
        from life_sciences_ecology.clients import mgnify_client

        respx.get("https://www.ebi.ac.uk/metagenomics/api/v1/studies").respond(
            200, json={"data": [{"id": "MGYS00000001"}]},
        )
        result = await mgnify_client.search(server, "ocean")
        assert "data" in result
