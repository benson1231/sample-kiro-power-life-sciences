"""Unit tests for life-sciences-structural MCP server tools.

Uses ``respx`` to mock httpx responses, following the same pattern as
``life-sciences-common/tests/test_server.py``.
"""

from __future__ import annotations

import json

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-structural")
    yield srv
    await srv.cleanup()


# ---------------------------------------------------------------------------
# PDB tools
# ---------------------------------------------------------------------------


class TestPDBTools:
    @respx.mock
    async def test_pdb_search(self, server: BaseLifeSciencesServer):
        from life_sciences_structural.clients import pdb_client

        respx.post("https://search.rcsb.org/rcsbsearch/v2/query").respond(
            200,
            json={
                "result_set": [
                    {"identifier": "1BNA", "score": 1.0},
                    {"identifier": "4HHB", "score": 0.9},
                ],
                "total_count": 2,
            },
        )
        result = await pdb_client.search(server, "hemoglobin", 10)
        assert "result_set" in result
        assert len(result["result_set"]) == 2

    @respx.mock
    async def test_pdb_fetch(self, server: BaseLifeSciencesServer):
        from life_sciences_structural.clients import pdb_client

        respx.get("https://data.rcsb.org/rest/v1/core/entry/4HHB").respond(
            200,
            json={
                "rcsb_id": "4HHB",
                "struct": {"title": "THE CRYSTAL STRUCTURE OF HUMAN DEOXYHAEMOGLOBIN"},
                "rcsb_entry_info": {"resolution_combined": [1.74]},
            },
        )
        result = await pdb_client.fetch(server, "4HHB")
        assert result["rcsb_id"] == "4HHB"
        assert "struct" in result

    @respx.mock
    async def test_pdb_download(self, server: BaseLifeSciencesServer):
        from life_sciences_structural.clients import pdb_client

        pdb_text = "HEADER    OXYGEN TRANSPORT\nATOM      1  N   VAL A   1\nEND\n"
        respx.get("https://files.rcsb.org/download/4HHB.pdb").respond(
            200, text=pdb_text,
        )
        result = await pdb_client.download(server, "4HHB", "pdb")
        assert result["pdb_id"] == "4HHB"
        assert result["format"] == "pdb"
        assert "OXYGEN TRANSPORT" in result["data"]


# ---------------------------------------------------------------------------
# AlphaFold DB tools
# ---------------------------------------------------------------------------


class TestAlphaFoldTools:
    @respx.mock
    async def test_alphafold_lookup(self, server: BaseLifeSciencesServer):
        from life_sciences_structural.clients import alphafold_client

        respx.get("https://alphafold.ebi.ac.uk/api/prediction/P04637").respond(
            200,
            json=[
                {
                    "entryId": "AF-P04637-F1",
                    "uniprotAccession": "P04637",
                    "gene": "TP53",
                    "pdbUrl": "https://alphafold.ebi.ac.uk/files/AF-P04637-F1-model_v4.pdb",
                    "confidenceVersion": 4,
                }
            ],
        )
        result = await alphafold_client.lookup(server, "P04637")
        assert result["uniprotAccession"] == "P04637"
        assert result["entryId"] == "AF-P04637-F1"


# ---------------------------------------------------------------------------
# CATH tools
# ---------------------------------------------------------------------------


class TestCATHTools:
    @respx.mock
    async def test_cath_classify(self, server: BaseLifeSciencesServer):
        from life_sciences_structural.clients import cath_client

        respx.get("https://www.cathdb.info/api/rest/id/1cukA01").respond(
            200,
            json={
                "data": {
                    "domain_id": "1cukA01",
                    "class": "1",
                    "architecture": "10",
                    "topology": "8",
                    "homologous_superfamily": "10",
                }
            },
        )
        result = await cath_client.classify(server, "1cukA01")
        assert result["data"]["domain_id"] == "1cukA01"


# ---------------------------------------------------------------------------
# SCOP tools
# ---------------------------------------------------------------------------


class TestSCOPTools:
    @respx.mock
    async def test_scop_classify(self, server: BaseLifeSciencesServer):
        from life_sciences_structural.clients import scop_client

        respx.get("https://scop.mrc-lmb.cam.ac.uk/api/pdb/4hhb").respond(
            200,
            json={
                "entries": [
                    {
                        "sunid": 14982,
                        "sccs": "a.1.1.2",
                        "description": "Hemoglobin, alpha-chain",
                    }
                ]
            },
        )
        result = await scop_client.classify(server, "4HHB")
        assert "entries" in result
        assert result["entries"][0]["sccs"] == "a.1.1.2"
