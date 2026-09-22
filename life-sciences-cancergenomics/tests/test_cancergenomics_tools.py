"""Unit tests for life-sciences-cancergenomics MCP server tools.

Uses ``respx`` to mock httpx responses, following the same pattern as
``life-sciences-genomics/tests/test_genomics_tools.py``.
"""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import RateLimitError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-cancergenomics")
    yield srv
    await srv.cleanup()


# ---------------------------------------------------------------------------
# search_studies
# ---------------------------------------------------------------------------


class TestSearchStudies:
    @respx.mock
    async def test_search_studies_filters_client_side(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get("https://www.cbioportal.org/api/studies").respond(
            200,
            json=[
                {
                    "studyId": "skcm_tcga",
                    "name": "Skin Cutaneous Melanoma (TCGA)",
                    "allSampleCount": 448,
                    "description": "TCGA melanoma cohort",
                    "citation": "TCGA 2015",
                    "referenceGenome": "hg19",
                },
                {
                    "studyId": "brca_tcga",
                    "name": "Breast Invasive Carcinoma (TCGA)",
                    "allSampleCount": 1084,
                    "description": "TCGA breast cohort",
                    "citation": "TCGA 2012",
                    "referenceGenome": "hg19",
                },
            ],
        )
        result = await cbioportal_client.search_studies(server, "melanoma")
        assert len(result["studies"]) == 1
        assert result["studies"][0]["study_id"] == "skcm_tcga"
        assert "1 studies matching 'melanoma'" in result["summary"]
        assert "448 total samples" in result["summary"]


# ---------------------------------------------------------------------------
# get_study_details
# ---------------------------------------------------------------------------


class TestGetStudyDetails:
    @respx.mock
    async def test_get_study_details(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get("https://www.cbioportal.org/api/studies/skcm_tcga").respond(
            200, json={"studyId": "skcm_tcga", "name": "Melanoma"},
        )
        respx.get(
            "https://www.cbioportal.org/api/studies/skcm_tcga/molecular-profiles"
        ).respond(
            200,
            json=[
                {
                    "molecularProfileId": "skcm_tcga_mutations",
                    "name": "Mutations",
                    "molecularAlterationType": "MUTATION_EXTENDED",
                }
            ],
        )
        respx.get(
            "https://www.cbioportal.org/api/studies/skcm_tcga/sample-lists"
        ).respond(
            200,
            json=[
                {
                    "sampleListId": "skcm_tcga_all",
                    "name": "All samples",
                    "description": "All tumor samples",
                }
            ],
        )
        result = await cbioportal_client.get_study_details(server, "skcm_tcga")
        assert result["study"]["studyId"] == "skcm_tcga"
        assert result["molecular_profiles"][0]["id"] == "skcm_tcga_mutations"
        assert result["sample_lists"][0]["id"] == "skcm_tcga_all"

    async def test_invalid_study_id_rejected(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        with pytest.raises(ValueError):
            await cbioportal_client.get_study_details(server, "../etc/passwd")


# ---------------------------------------------------------------------------
# get_molecular_profiles
# ---------------------------------------------------------------------------


class TestGetMolecularProfiles:
    @respx.mock
    async def test_get_molecular_profiles(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get(
            "https://www.cbioportal.org/api/studies/skcm_tcga/molecular-profiles"
        ).respond(
            200,
            json=[
                {
                    "molecularProfileId": "skcm_tcga_mutations",
                    "name": "Mutations",
                    "molecularAlterationType": "MUTATION_EXTENDED",
                    "datatype": "MAF",
                }
            ],
        )
        result = await cbioportal_client.get_molecular_profiles(server, "skcm_tcga")
        assert result[0]["id"] == "skcm_tcga_mutations"
        assert result[0]["datatype"] == "MAF"


# ---------------------------------------------------------------------------
# get_clinical_data
# ---------------------------------------------------------------------------


class TestGetClinicalData:
    @respx.mock
    async def test_list_attributes_when_no_attribute_id(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get(
            "https://www.cbioportal.org/api/studies/skcm_tcga/clinical-attributes"
        ).respond(
            200,
            json=[
                {
                    "clinicalAttributeId": "MUTATION_COUNT",
                    "displayName": "Mutation Count",
                    "datatype": "NUMBER",
                }
            ],
        )
        result = await cbioportal_client.get_clinical_data(server, "skcm_tcga")
        assert result["available_attributes"][0]["id"] == "MUTATION_COUNT"

    @respx.mock
    async def test_fetch_clinical_data_values(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get(
            "https://www.cbioportal.org/api/studies/skcm_tcga/clinical-data"
        ).respond(
            200,
            json=[{"sampleId": "S1", "value": "42"}, {"sampleId": "S2", "value": "17"}],
        )
        result = await cbioportal_client.get_clinical_data(
            server, "skcm_tcga", "MUTATION_COUNT",
        )
        assert result["attribute_id"] == "MUTATION_COUNT"
        assert len(result["data"]) == 2


# ---------------------------------------------------------------------------
# search_genes
# ---------------------------------------------------------------------------


class TestSearchGenes:
    @respx.mock
    async def test_search_genes(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get("https://www.cbioportal.org/api/genes").respond(
            200,
            json=[
                {"entrezGeneId": 7157, "hugoGeneSymbol": "TP53", "type": "protein-coding"}
            ],
        )
        result = await cbioportal_client.search_genes(server, "TP53")
        assert result[0]["hugoGeneSymbol"] == "TP53"


# ---------------------------------------------------------------------------
# compare_mutation_burden
# ---------------------------------------------------------------------------


class TestCompareMutationBurden:
    @respx.mock
    async def test_compare_mutation_burden(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get(
            "https://www.cbioportal.org/api/studies/skcm_tcga/clinical-data"
        ).respond(
            200,
            json=[
                {"sampleId": "S1", "value": "150"},
                {"sampleId": "S2", "value": "40"},
                {"sampleId": "S3", "value": "1200"},
                {"sampleId": "S4", "value": "not_a_number"},
            ],
        )
        result = await cbioportal_client.compare_mutation_burden(server, "skcm_tcga")
        assert result["samples_with_tmb_data"] == 3
        assert result["max_mutations"] == 1200
        assert result["min_mutations"] == 40
        assert result["high_tmb_above_100"] == 2
        assert result["distribution"]["1000+"] == 1
        assert result["median_mutations"] == 150

    @respx.mock
    async def test_compare_mutation_burden_no_data(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get(
            "https://www.cbioportal.org/api/studies/skcm_tcga/clinical-data"
        ).respond(200, json=[])
        result = await cbioportal_client.compare_mutation_burden(server, "skcm_tcga")
        assert "error_message" in result


# ---------------------------------------------------------------------------
# list_cancer_types
# ---------------------------------------------------------------------------


class TestListCancerTypes:
    @respx.mock
    async def test_list_cancer_types(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get("https://www.cbioportal.org/api/cancer-types").respond(
            200,
            json=[
                {"cancerTypeId": "skcm", "name": "Cutaneous Melanoma", "parent": "mel"}
            ],
        )
        result = await cbioportal_client.list_cancer_types(server)
        assert result[0]["id"] == "skcm"
        assert result[0]["parent"] == "mel"


# ---------------------------------------------------------------------------
# Server wiring
# ---------------------------------------------------------------------------


class TestServerWiring:
    async def test_all_tools_registered(self):
        from life_sciences_cancergenomics.server import TOOLS

        names = {t.name for t in TOOLS}
        assert names == {
            "cbioportal_search_studies",
            "cbioportal_get_study_details",
            "cbioportal_get_molecular_profiles",
            "cbioportal_get_clinical_data",
            "cbioportal_search_genes",
            "cbioportal_compare_mutation_burden",
            "cbioportal_list_cancer_types",
        }

    async def test_dispatch_covers_all_tools(self):
        from life_sciences_cancergenomics.server import (
            TOOLS,
            CancerGenomicsServer,
        )

        srv = CancerGenomicsServer()
        try:
            assert set(srv._dispatch.keys()) == {t.name for t in TOOLS}
        finally:
            await srv.cleanup()


# ---------------------------------------------------------------------------
# Rate-limit retry behaviour
# ---------------------------------------------------------------------------


class TestRateLimitRetry:
    @respx.mock
    async def test_rate_limit_retry(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get("https://www.cbioportal.org/api/cancer-types").side_effect = [
            httpx.Response(429, headers={"Retry-After": "0"}),
            httpx.Response(200, json=[{"cancerTypeId": "skcm", "name": "Melanoma"}]),
        ]
        result = await cbioportal_client.list_cancer_types(server)
        assert result[0]["id"] == "skcm"

    @respx.mock
    async def test_rate_limit_exhaustion(self, server: BaseLifeSciencesServer):
        from life_sciences_cancergenomics.clients import cbioportal_client

        respx.get("https://www.cbioportal.org/api/cancer-types").side_effect = [
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),
            httpx.Response(429),
        ]
        with pytest.raises(RateLimitError):
            await cbioportal_client.list_cancer_types(server)
