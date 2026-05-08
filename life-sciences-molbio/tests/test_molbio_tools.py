"""Unit tests for life-sciences-molbio MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-molbio")
    yield srv
    await srv.cleanup()


class TestBLASTSearch:
    @respx.mock
    async def test_blast_search(self, server: BaseLifeSciencesServer):
        from life_sciences_molbio.clients import blast_client

        respx.post("https://blast.ncbi.nlm.nih.gov/Blast.cgi").respond(
            200, text="RID = ABC123\nRTOE = 30\n",
        )
        result = await blast_client.search(server, "ATGCGATCGATCG")
        assert result["rid"] == "ABC123"
        assert result["status"] == "submitted"


class TestBLASTResults:
    @respx.mock
    async def test_blast_results_waiting(self, server: BaseLifeSciencesServer):
        from life_sciences_molbio.clients import blast_client

        respx.get("https://blast.ncbi.nlm.nih.gov/Blast.cgi").respond(
            200, text="Status=WAITING\n",
        )
        result = await blast_client.results(server, "ABC123")
        assert result["status"] == "waiting"


class TestMSAAlign:
    @respx.mock
    async def test_msa_align(self, server: BaseLifeSciencesServer):
        from life_sciences_molbio.clients import msa_client

        respx.post("https://www.ebi.ac.uk/Tools/services/rest/clustalo/run").respond(
            200, text="clustalo-R20240101-123456",
        )
        result = await msa_client.align(server, ["MVLSPADKTN", "MVHLTPEEKS"])
        assert result["job_id"] == "clustalo-R20240101-123456"
        assert result["tool"] == "clustalo"


class TestHMMERSearch:
    @respx.mock
    async def test_hmmer_search(self, server: BaseLifeSciencesServer):
        from life_sciences_molbio.clients import hmmer_client

        respx.post("https://www.ebi.ac.uk/Tools/hmmer/search/hmmscan").respond(
            200, json={"results": {"hits": [{"name": "PF00069"}]}},
        )
        result = await hmmer_client.search(server, "MVLSPADKTN")
        assert "results" in result


class TestPrimer3Design:
    @respx.mock
    async def test_primer3_design(self, server: BaseLifeSciencesServer):
        from life_sciences_molbio.clients import primer_client

        respx.post(
            "https://primer3.ut.ee/cgi-bin/primer3/primer3web_results.cgi"
        ).respond(200, text="PRIMER_LEFT_0=ATGCGATCG\nPRIMER_RIGHT_0=CGATCGCAT")
        result = await primer_client.design(server, "ATGCGATCGATCGATCG")
        assert result["status"] == "completed"


class TestRestrictionAnalysis:
    async def test_restriction_analysis(self, server: BaseLifeSciencesServer):
        from life_sciences_molbio.clients import restriction_client

        result = await restriction_client.analysis(
            server, "ATGAATTCGGATCCAAGCTT", ["EcoRI", "BamHI", "HindIII"],
        )
        assert result["sequence_length"] == 20
        assert len(result["results"]) == 3
        # EcoRI cuts at GAATTC (pos 2), BamHI at GGATCC (pos 8), HindIII at AAGCTT (pos 14)
        assert result["results"][0]["num_cuts"] == 1
        assert result["results"][1]["num_cuts"] == 1
        assert result["results"][2]["num_cuts"] == 1


class TestREBASEEnzyme:
    @respx.mock
    async def test_rebase_enzyme(self, server: BaseLifeSciencesServer):
        from life_sciences_molbio.clients import rebase_client

        respx.get("https://rebase.neb.com/rebase/enz/EcoRI.html").respond(
            200, text="<html>EcoRI info</html>",
        )
        result = await rebase_client.enzyme(server, "EcoRI")
        assert result["enzyme"] == "EcoRI"
        assert result["source"] == "REBASE"


class TestCloningDesign:
    async def test_cloning_design(self, server: BaseLifeSciencesServer):
        from life_sciences_molbio.clients import restriction_client

        result = await restriction_client.cloning_design(
            server,
            vector="ATGAATTCGGATCCAAGCTT",
            insert="ATGCCCGGGAAATTT",
            sites=["EcoRI", "BamHI"],
        )
        assert result["vector_length"] == 20
        assert result["insert_length"] == 15
        assert len(result["restriction_sites"]) == 2
