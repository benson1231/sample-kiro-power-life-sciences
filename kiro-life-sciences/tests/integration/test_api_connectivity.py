"""Integration tests for MCP server API connectivity.

Tests that each MCP server's client modules can construct valid URLs
and handle mocked responses correctly.

**Validates: Requirements 10.5, 10.6**
"""

from __future__ import annotations

import httpx
import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import RateLimitError


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-connectivity")
    yield srv
    await srv.cleanup()


class TestGenomicsConnectivity:
    @respx.mock
    async def test_ncbi_url_construction(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import ncbi_client

        route = respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").respond(
            200, json={"esearchresult": {"idlist": [], "count": "0"}},
        )
        await ncbi_client.search(server, "gene", "TP53", 5)
        assert route.called


class TestProteomicsConnectivity:
    @respx.mock
    async def test_uniprot_url_construction(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import uniprot_client

        route = respx.get(url__startswith="https://rest.uniprot.org/").respond(
            200, json={"results": []},
        )
        await uniprot_client.search(server, "BRCA1")
        assert route.called


class TestStructuralConnectivity:
    @respx.mock
    async def test_pdb_url_construction(self, server: BaseLifeSciencesServer):
        from life_sciences_structural.clients import pdb_client

        route = respx.post("https://search.rcsb.org/rcsbsearch/v2/query").respond(
            200, json={"result_set": []},
        )
        await pdb_client.search(server, "kinase")
        assert route.called


class TestEcologyConnectivity:
    @respx.mock
    async def test_gbif_url_construction(self, server: BaseLifeSciencesServer):
        from life_sciences_ecology.clients import gbif_client

        route = respx.get("https://api.gbif.org/v1/occurrence/search").respond(
            200, json={"results": [], "count": 0},
        )
        await gbif_client.occurrences(server, "Homo sapiens")
        assert route.called


class TestRateLimitRetryIntegration:
    @respx.mock
    async def test_rate_limit_retry_then_success(self, server: BaseLifeSciencesServer):
        """Verify retry on 429 then success on 200."""
        from life_sciences_genomics.clients import ncbi_client

        respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").side_effect = [
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"esearchresult": {"idlist": ["1"], "count": "1"}}),
        ]
        result = await ncbi_client.search(server, "gene", "TP53", 5)
        assert result["esearchresult"]["count"] == "1"

    @respx.mock
    async def test_rate_limit_exhaustion(self, server: BaseLifeSciencesServer):
        """Verify RateLimitError after retries exhausted."""
        from life_sciences_genomics.clients import ncbi_client

        respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").side_effect = [
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),
        ]
        with pytest.raises(RateLimitError):
            await ncbi_client.search(server, "gene", "TP53", 5)
