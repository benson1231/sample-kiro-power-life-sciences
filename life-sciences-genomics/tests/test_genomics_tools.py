"""Unit tests for life-sciences-genomics MCP server tools.

Uses ``respx`` to mock httpx responses, following the same pattern as
``life-sciences-common/tests/test_server.py``.
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import AuthenticationError, RateLimitError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-genomics")
    yield srv
    await srv.cleanup()


# ---------------------------------------------------------------------------
# NCBI tools
# ---------------------------------------------------------------------------


class TestNCBISearch:
    @respx.mock
    async def test_ncbi_search(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import ncbi_client

        respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").respond(
            200,
            json={"esearchresult": {"idlist": ["12345", "67890"], "count": "2"}},
        )
        result = await ncbi_client.search(server, "gene", "BRCA1", 10)
        assert "esearchresult" in result
        assert result["esearchresult"]["idlist"] == ["12345", "67890"]

    @respx.mock
    async def test_ncbi_fetch_sequence(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import ncbi_client

        fasta_text = ">NM_007294.4 Homo sapiens BRCA1\nATGGATTTATCTGCTCTTCG\n"
        respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi").respond(
            200, text=fasta_text,
        )
        result = await ncbi_client.fetch_sequence(server, "NM_007294.4", "fasta")
        assert result["accession"] == "NM_007294.4"
        assert result["format"] == "fasta"
        assert "BRCA1" in result["data"]

    @respx.mock
    async def test_ncbi_pubmed_search(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import ncbi_client

        # Mock esearch
        respx.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        ).respond(
            200,
            json={"esearchresult": {"idlist": ["11111"], "count": "1"}},
        )
        # Mock esummary
        respx.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        ).respond(
            200,
            json={
                "result": {
                    "uids": ["11111"],
                    "11111": {"uid": "11111", "title": "BRCA1 study"},
                }
            },
        )
        result = await ncbi_client.pubmed_search(server, "BRCA1", 5)
        assert result["term"] == "BRCA1"
        assert result["count"] == 1
        assert "uids" in result["articles"]
        assert "11111" in result["articles"]


# ---------------------------------------------------------------------------
# Ensembl tools
# ---------------------------------------------------------------------------


class TestEnsemblTools:
    @respx.mock
    async def test_ensembl_gene_lookup(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import ensembl_client

        respx.get("https://rest.ensembl.org/lookup/symbol/homo_sapiens/BRCA2").respond(
            200,
            json={
                "id": "ENSG00000139618",
                "display_name": "BRCA2",
                "species": "homo_sapiens",
                "biotype": "protein_coding",
            },
        )
        result = await ensembl_client.gene_lookup(server, "BRCA2")
        assert result["id"] == "ENSG00000139618"
        assert result["display_name"] == "BRCA2"

    @respx.mock
    async def test_ensembl_variants(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import ensembl_client

        region = "7:140424943-140624564"
        respx.get(
            f"https://rest.ensembl.org/overlap/region/homo_sapiens/{region}"
        ).respond(
            200,
            json=[
                {"id": "rs113488022", "consequence_type": "missense_variant"},
            ],
        )
        result = await ensembl_client.variants(server, region)
        assert result["region"] == region
        assert len(result["variants"]) == 1
        assert result["variants"][0]["id"] == "rs113488022"


# ---------------------------------------------------------------------------
# ClinVar tools
# ---------------------------------------------------------------------------


class TestClinVarTools:
    @respx.mock
    async def test_clinvar_search(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import clinvar_client

        respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").respond(
            200,
            json={"esearchresult": {"idlist": ["99999"], "count": "1"}},
        )
        result = await clinvar_client.search(server, "BRCA1", 10)
        assert "esearchresult" in result
        assert "99999" in result["esearchresult"]["idlist"]


# ---------------------------------------------------------------------------
# COSMIC tools (auth required)
# ---------------------------------------------------------------------------


class TestCOSMICTools:
    async def test_cosmic_search_requires_auth(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_genomics.clients import cosmic_client

        monkeypatch.delenv("COSMIC_API_KEY", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            await cosmic_client.search(server, "BRAF")
        assert "COSMIC_API_KEY" in exc_info.value.message
        assert exc_info.value.obtain_url == "https://cancer.sanger.ac.uk/cosmic/register"

    @respx.mock
    async def test_cosmic_search_with_key(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_genomics.clients import cosmic_client

        monkeypatch.setenv("COSMIC_API_KEY", "test-key-123")
        respx.get("https://cancer.sanger.ac.uk/cosmic/api/v1/mutations").respond(
            200,
            json={"mutations": [{"gene": "BRAF", "mutation": "V600E"}]},
        )
        result = await cosmic_client.search(server, "BRAF")
        assert "mutations" in result


# ---------------------------------------------------------------------------
# gnomAD tools (GraphQL)
# ---------------------------------------------------------------------------


class TestGnomADTools:
    @respx.mock
    async def test_gnomad_variant(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import gnomad_client

        respx.post("https://gnomad.broadinstitute.org/api/").respond(
            200,
            json={
                "data": {
                    "variant": {
                        "variant_id": "1-55516888-G-A",
                        "genome": {"af": 0.001},
                    }
                }
            },
        )
        result = await gnomad_client.variant(server, "1-55516888-G-A")
        assert "data" in result
        assert result["data"]["variant"]["variant_id"] == "1-55516888-G-A"


# ---------------------------------------------------------------------------
# dbSNP tools
# ---------------------------------------------------------------------------


class TestDbSNPTools:
    @respx.mock
    async def test_dbsnp_lookup(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import dbsnp_client

        respx.get("https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/328").respond(
            200,
            json={
                "refsnp_id": "328",
                "primary_snapshot_data": {"allele_annotations": []},
            },
        )
        result = await dbsnp_client.lookup(server, "rs328")
        assert result["refsnp_id"] == "328"


# ---------------------------------------------------------------------------
# ENCODE tools
# ---------------------------------------------------------------------------


class TestENCODETools:
    @respx.mock
    async def test_encode_search(self, server: BaseLifeSciencesServer):
        from life_sciences_genomics.clients import encode_client

        respx.get("https://www.encodeproject.org/search/").respond(
            200,
            json={
                "@graph": [
                    {"accession": "ENCSR000AAA", "assay_title": "ChIP-seq"}
                ],
                "total": 1,
            },
        )
        result = await encode_client.search(server, biosample="K562", assay="ChIP-seq")
        assert result["total"] == 1
        assert result["@graph"][0]["accession"] == "ENCSR000AAA"


# ---------------------------------------------------------------------------
# Rate-limit retry behaviour
# ---------------------------------------------------------------------------


class TestRateLimitRetry:
    @respx.mock
    async def test_rate_limit_retry(self, server: BaseLifeSciencesServer):
        """Mock 429 then 200 to verify retry behaviour at the client level."""
        from life_sciences_genomics.clients import ncbi_client

        respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").side_effect = [
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json={"esearchresult": {"idlist": ["1"], "count": "1"}}),
        ]
        result = await ncbi_client.search(server, "gene", "TP53", 5)
        assert "esearchresult" in result

    @respx.mock
    async def test_rate_limit_exhaustion(self, server: BaseLifeSciencesServer):
        """Verify RateLimitError is raised after retries are exhausted."""
        from life_sciences_genomics.clients import ncbi_client

        respx.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi").side_effect = [
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),
        ]
        with pytest.raises(RateLimitError):
            await ncbi_client.search(server, "gene", "TP53", 5)
