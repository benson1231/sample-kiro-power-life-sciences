"""Unit tests for life-sciences-immunology MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import AuthenticationError


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-immunology")
    yield srv
    await srv.cleanup()


class TestIEDBSearch:
    @respx.mock
    async def test_iedb_search(self, server: BaseLifeSciencesServer):
        from life_sciences_immunology.clients import iedb_client

        respx.get("https://query-api.iedb.org/epitope_search").respond(
            200, json=[{"epitope_id": 1, "linear_sequence": "SIINFEKL"}],
        )
        result = await iedb_client.search(server, "SIINFEKL")
        assert isinstance(result, list)
        assert result[0]["linear_sequence"] == "SIINFEKL"


class TestImmPortSearch:
    async def test_immport_requires_auth(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_immunology.clients import immport_client

        monkeypatch.delenv("IMMPORT_USERNAME", raising=False)
        monkeypatch.delenv("IMMPORT_PASSWORD", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            await immport_client.search(server, "influenza")
        assert "IMMPORT_USERNAME" in exc_info.value.message

    @respx.mock
    async def test_immport_search_with_creds(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_immunology.clients import immport_client

        monkeypatch.setenv("IMMPORT_USERNAME", "user")
        monkeypatch.setenv("IMMPORT_PASSWORD", "pass")
        respx.post("https://api.immport.org/auth/token").respond(
            200, json={"token": "tok-123"},
        )
        respx.get("https://api.immport.org/data/query/result/study").respond(
            200, json={"studies": [{"study_id": "SDY1"}]},
        )
        result = await immport_client.search(server, "influenza")
        assert "studies" in result


class TestIMGTSearch:
    @respx.mock
    async def test_imgt_search(self, server: BaseLifeSciencesServer):
        from life_sciences_immunology.clients import imgt_client

        respx.get("https://www.imgt.org/genedb/GENElect").respond(
            200, text="<html>IGHV1-2 gene info</html>",
        )
        result = await imgt_client.search(server, "IGHV1-2")
        assert result["gene"] == "IGHV1-2"
        assert result["source"] == "IMGT"


class TestAbYsisAnalyze:
    @respx.mock
    async def test_abysis_analyze(self, server: BaseLifeSciencesServer):
        from life_sciences_immunology.clients import abysis_client

        respx.post("https://www.abysis.org/api/analyze").respond(
            200, json={"chain_type": "heavy", "cdr_regions": ["CDR1", "CDR2", "CDR3"]},
        )
        result = await abysis_client.analyze(server, "EVQLVESGGGLVQPGG")
        assert result["chain_type"] == "heavy"
