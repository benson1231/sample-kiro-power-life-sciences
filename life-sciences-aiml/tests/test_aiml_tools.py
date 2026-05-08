"""Unit tests for life-sciences-aiml MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-aiml")
    yield srv
    await srv.cleanup()


class TestESMEmbeddings:
    @respx.mock
    async def test_esm_embeddings(self, server: BaseLifeSciencesServer):
        from life_sciences_aiml.clients import esm_client

        respx.post("https://api.esmatlas.com/foldSequence/v1/pdb/").respond(
            200, text="ATOM      1  N   MET A   1\n",
        )
        result = await esm_client.embeddings(server, "MVLSPADKTN")
        assert result["embedding_available"] is True


class TestAlphaFoldPredict:
    @respx.mock
    async def test_alphafold_predict(self, server: BaseLifeSciencesServer):
        from life_sciences_aiml.clients import alphafold_client

        respx.post("https://alphafold.ebi.ac.uk/api/prediction/submit").respond(
            200, json={"job_id": "af-123", "status": "submitted"},
        )
        result = await alphafold_client.predict(server, "MVLSPADKTN")
        assert result["job_id"] == "af-123"


class TestAlphaFoldStatus:
    @respx.mock
    async def test_alphafold_status(self, server: BaseLifeSciencesServer):
        from life_sciences_aiml.clients import alphafold_client

        respx.get("https://alphafold.ebi.ac.uk/api/prediction/af-123").respond(
            200, json={"job_id": "af-123", "status": "completed"},
        )
        result = await alphafold_client.status(server, "af-123")
        assert result["status"] == "completed"


class TestBioNLPEntities:
    @respx.mock
    async def test_bionlp_entities(self, server: BaseLifeSciencesServer):
        from life_sciences_aiml.clients import bionlp_client

        respx.post("https://bionlp.nlm.nih.gov/api/ner").respond(
            200, json={"entities": [{"text": "BRCA1", "type": "Gene"}]},
        )
        result = await bionlp_client.entities(server, "BRCA1 is a tumor suppressor")
        assert result["entities"][0]["text"] == "BRCA1"


class TestBioNLPQA:
    @respx.mock
    async def test_bionlp_qa(self, server: BaseLifeSciencesServer):
        from life_sciences_aiml.clients import bionlp_client

        respx.post("https://bionlp.nlm.nih.gov/api/qa").respond(
            200, json={"answer": "BRCA1", "confidence": 0.95},
        )
        result = await bionlp_client.qa(
            server, "What gene is mutated?", "BRCA1 mutations cause cancer.",
        )
        assert result["answer"] == "BRCA1"
