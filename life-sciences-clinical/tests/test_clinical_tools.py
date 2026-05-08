"""Unit tests for life-sciences-clinical MCP server tools.

Uses ``respx`` to mock httpx responses, following the same pattern as
``life-sciences-common/tests/test_server.py``.
"""

from __future__ import annotations

import json

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import AuthenticationError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-clinical")
    yield srv
    await srv.cleanup()


# ---------------------------------------------------------------------------
# OMIM tools (auth required)
# ---------------------------------------------------------------------------


class TestOMIMTools:
    async def test_omim_search_requires_auth(
        self, server: BaseLifeSciencesServer, monkeypatch,
    ):
        from life_sciences_clinical.clients import omim_client

        monkeypatch.delenv("OMIM_API_KEY", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            await omim_client.search(server, "BRCA1")
        assert "OMIM_API_KEY" in exc_info.value.message
        assert exc_info.value.obtain_url == "https://www.omim.org/api"

    @respx.mock
    async def test_omim_search_with_key(
        self, server: BaseLifeSciencesServer, monkeypatch,
    ):
        from life_sciences_clinical.clients import omim_client

        monkeypatch.setenv("OMIM_API_KEY", "test-omim-key")
        respx.get("https://api.omim.org/api/entry/search").respond(
            200,
            json={
                "omim": {
                    "searchResponse": {
                        "totalResults": 1,
                        "entryList": [
                            {"entry": {"mimNumber": 113705, "titles": {"preferredTitle": "BRCA1"}}}
                        ],
                    }
                }
            },
        )
        result = await omim_client.search(server, "BRCA1", 10)
        assert "omim" in result


# ---------------------------------------------------------------------------
# DrugBank tools (auth required)
# ---------------------------------------------------------------------------


class TestDrugBankTools:
    async def test_drugbank_search_requires_auth(
        self, server: BaseLifeSciencesServer, monkeypatch,
    ):
        from life_sciences_clinical.clients import drugbank_client

        monkeypatch.delenv("DRUGBANK_API_KEY", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            await drugbank_client.search(server, "aspirin")
        assert "DRUGBANK_API_KEY" in exc_info.value.message
        assert exc_info.value.obtain_url == "https://go.drugbank.com/public_users/sign_up"

    @respx.mock
    async def test_drugbank_search_with_key(
        self, server: BaseLifeSciencesServer, monkeypatch,
    ):
        from life_sciences_clinical.clients import drugbank_client

        monkeypatch.setenv("DRUGBANK_API_KEY", "test-drugbank-key")
        respx.get("https://go.drugbank.com/api/v1/drugs").respond(
            200,
            json=[
                {"drugbank_id": "DB00945", "name": "Aspirin", "cas_number": "50-78-2"}
            ],
        )
        result = await drugbank_client.search(server, "aspirin", 10)
        assert isinstance(result, list)
        assert result[0]["drugbank_id"] == "DB00945"


# ---------------------------------------------------------------------------
# ChEMBL tools
# ---------------------------------------------------------------------------


class TestChEMBLTools:
    @respx.mock
    async def test_chembl_search(self, server: BaseLifeSciencesServer):
        from life_sciences_clinical.clients import chembl_client

        respx.get(
            "https://www.ebi.ac.uk/chembl/api/data/molecule/search"
        ).respond(
            200,
            json={
                "molecules": [
                    {
                        "molecule_chembl_id": "CHEMBL25",
                        "pref_name": "ASPIRIN",
                    }
                ],
                "page_meta": {"total_count": 1},
            },
        )
        result = await chembl_client.search(server, "aspirin", 10)
        assert "molecules" in result

    @respx.mock
    async def test_chembl_bioactivity(self, server: BaseLifeSciencesServer):
        from life_sciences_clinical.clients import chembl_client

        respx.get("https://www.ebi.ac.uk/chembl/api/data/activity").respond(
            200,
            json={
                "activities": [
                    {
                        "molecule_chembl_id": "CHEMBL25",
                        "target_chembl_id": "CHEMBL2094253",
                        "standard_type": "IC50",
                        "standard_value": "100",
                    }
                ],
                "page_meta": {"total_count": 1},
            },
        )
        result = await chembl_client.bioactivity(server, "CHEMBL25", 100)
        assert "activities" in result


# ---------------------------------------------------------------------------
# PharmGKB tools
# ---------------------------------------------------------------------------


class TestPharmGKBTools:
    @respx.mock
    async def test_pharmgkb_search(self, server: BaseLifeSciencesServer):
        from life_sciences_clinical.clients import pharmgkb_client

        respx.get("https://api.pharmgkb.org/v1/data/search").respond(
            200,
            json={
                "data": [
                    {"id": "PA443560", "name": "warfarin", "type": "Drug"}
                ],
                "totalCount": 1,
            },
        )
        result = await pharmgkb_client.search(server, "warfarin")
        assert "data" in result
        assert result["data"][0]["name"] == "warfarin"


# ---------------------------------------------------------------------------
# OpenTargets tools (GraphQL)
# ---------------------------------------------------------------------------


class TestOpenTargetsTools:
    @respx.mock
    async def test_opentargets_search(self, server: BaseLifeSciencesServer):
        from life_sciences_clinical.clients import opentargets_client

        respx.post(
            "https://api.platform.opentargets.org/api/v4/graphql"
        ).respond(
            200,
            json={
                "data": {
                    "search": {
                        "total": 1,
                        "hits": [
                            {
                                "id": "ENSG00000141510",
                                "name": "TP53",
                                "entity": "target",
                                "description": "Tumor protein p53",
                            }
                        ],
                    }
                }
            },
        )
        result = await opentargets_client.search(server, "TP53", 10)
        assert "data" in result
        assert result["data"]["search"]["total"] == 1


# ---------------------------------------------------------------------------
# FDA FAERS tools
# ---------------------------------------------------------------------------


class TestFDAFAERSTools:
    @respx.mock
    async def test_fda_faers_search(self, server: BaseLifeSciencesServer):
        from life_sciences_clinical.clients import fda_faers_client

        respx.get("https://api.fda.gov/drug/event.json").respond(
            200,
            json={
                "meta": {"results": {"total": 100}},
                "results": [
                    {
                        "safetyreportid": "10001",
                        "patient": {
                            "drug": [{"openfda": {"generic_name": ["ASPIRIN"]}}]
                        },
                    }
                ],
            },
        )
        result = await fda_faers_client.search(server, "aspirin", 10)
        assert "results" in result
        assert result["meta"]["results"]["total"] == 100


# ---------------------------------------------------------------------------
# ClinicalTrials.gov tools
# ---------------------------------------------------------------------------


class TestClinicalTrialsTools:
    @respx.mock
    async def test_clinicaltrials_search(self, server: BaseLifeSciencesServer):
        from life_sciences_clinical.clients import clinicaltrials_client

        respx.get("https://clinicaltrials.gov/api/v2/studies").respond(
            200,
            json={
                "studies": [
                    {
                        "protocolSection": {
                            "identificationModule": {
                                "nctId": "NCT00000001",
                                "briefTitle": "Breast Cancer Trial",
                            }
                        }
                    }
                ],
                "totalCount": 1,
            },
        )
        result = await clinicaltrials_client.search(server, "breast cancer", 10)
        assert "studies" in result
        assert result["totalCount"] == 1
