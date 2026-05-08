"""Unit tests for life-sciences-cheminformatics MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import AuthenticationError


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-cheminformatics")
    yield srv
    await srv.cleanup()


class TestPubChemSearch:
    @respx.mock
    async def test_pubchem_search(self, server: BaseLifeSciencesServer):
        from life_sciences_cheminformatics.clients import pubchem_client

        respx.get(
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/cids/JSON"
        ).respond(200, json={"IdentifierList": {"CID": [2244]}})
        result = await pubchem_client.search(server, "aspirin")
        assert result["query"] == "aspirin"
        assert 2244 in result["cids"]


class TestPubChemProperties:
    @respx.mock
    async def test_pubchem_properties(self, server: BaseLifeSciencesServer):
        from life_sciences_cheminformatics.clients import pubchem_client

        url_pattern = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/"
        respx.get(url__startswith=url_pattern).respond(
            200,
            json={"PropertyTable": {"Properties": [{"CID": 2244, "MolecularWeight": 180.16}]}},
        )
        result = await pubchem_client.properties(server, "2244")
        assert "PropertyTable" in result


class TestChemSpiderSearch:
    async def test_chemspider_requires_auth(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_cheminformatics.clients import chemspider_client

        monkeypatch.delenv("CHEMSPIDER_API_KEY", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            await chemspider_client.search(server, "aspirin")
        assert "CHEMSPIDER_API_KEY" in exc_info.value.message

    @respx.mock
    async def test_chemspider_search_with_key(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_cheminformatics.clients import chemspider_client

        monkeypatch.setenv("CHEMSPIDER_API_KEY", "test-key")
        respx.post("https://api.rsc.org/compounds/v1/filter/name").respond(
            200, json={"queryId": "q123"},
        )
        respx.get("https://api.rsc.org/compounds/v1/filter/q123/results").respond(
            200, json={"results": [{"csid": 2157}]},
        )
        result = await chemspider_client.search(server, "aspirin")
        assert "results" in result


class TestZINCSearch:
    @respx.mock
    async def test_zinc_search(self, server: BaseLifeSciencesServer):
        from life_sciences_cheminformatics.clients import zinc_client

        respx.get("https://zinc15.docking.org/api/substances/search/").respond(
            200, json={"results": [{"zinc_id": "ZINC000001"}]},
        )
        result = await zinc_client.search(server, "CCO")
        assert "results" in result


class TestRDKitDescriptors:
    async def test_rdkit_descriptors(self, server: BaseLifeSciencesServer):
        from life_sciences_cheminformatics.clients import rdkit_client

        result = await rdkit_client.descriptors(server, "c1ccccc1")
        assert result["smiles"] == "c1ccccc1"
        assert "heavy_atom_count" in result


class TestDockingSubmit:
    @respx.mock
    async def test_docking_submit(self, server: BaseLifeSciencesServer):
        from life_sciences_cheminformatics.clients import docking_client

        respx.post("https://www.swissdock.ch/api/docking").respond(
            200, json={"job_id": "dock-123", "status": "submitted"},
        )
        result = await docking_client.submit(server, "1ABC", "CCO")
        assert result["job_id"] == "dock-123"


class TestADMETPredict:
    @respx.mock
    async def test_admet_predict(self, server: BaseLifeSciencesServer):
        from life_sciences_cheminformatics.clients import admet_client

        respx.post("https://admetmesh.scbdd.com/api/predict").respond(
            200, json={"smiles": "CCO", "absorption": {"hia": 0.95}},
        )
        result = await admet_client.predict(server, "CCO")
        assert result["smiles"] == "CCO"
