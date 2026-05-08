"""Unit tests for life-sciences-healthcare MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer
from life_sciences_common.errors import AuthenticationError


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-healthcare")
    yield srv
    await srv.cleanup()


class TestFHIRSearch:
    @respx.mock
    async def test_fhir_search(self, server: BaseLifeSciencesServer):
        from life_sciences_healthcare.clients import fhir_client

        respx.get("https://hapi.fhir.org/baseR4/Patient").respond(
            200, json={"resourceType": "Bundle", "total": 1, "entry": [{"resource": {"id": "1"}}]},
        )
        result = await fhir_client.search(server, "Patient", {"name": "Smith"})
        assert result["resourceType"] == "Bundle"


class TestFHIRCreate:
    @respx.mock
    async def test_fhir_create(self, server: BaseLifeSciencesServer):
        from life_sciences_healthcare.clients import fhir_client

        respx.post("https://hapi.fhir.org/baseR4/Patient").respond(
            201, json={"resourceType": "Patient", "id": "123"},
        )
        result = await fhir_client.create(
            server, "Patient", {"resourceType": "Patient", "name": [{"family": "Smith"}]},
        )
        assert result["id"] == "123"


class TestHL7Parse:
    async def test_hl7_parse(self, server: BaseLifeSciencesServer):
        from life_sciences_healthcare.clients import hl7_client

        msg = "MSH|^~\\&|APP|FAC|APP|FAC|||ADT^A01||P|2.5\rPID|||12345||Smith^John"
        result = await hl7_client.parse(server, msg)
        assert result["segment_count"] == 2
        assert result["segments"][0]["segment"] == "MSH"


class TestHL7Generate:
    async def test_hl7_generate(self, server: BaseLifeSciencesServer):
        from life_sciences_healthcare.clients import hl7_client

        result = await hl7_client.generate(
            server,
            "ADT^A01",
            {
                "sending_app": "TestApp",
                "sending_facility": "TestFac",
                "patient": {"id": "12345", "name": "Smith^John", "dob": "19800101", "sex": "M"},
            },
        )
        assert result["segment_count"] == 2
        assert "MSH" in result["message"]
        assert "PID" in result["message"]


class TestOMOPSearch:
    @respx.mock
    async def test_omop_search(self, server: BaseLifeSciencesServer):
        from life_sciences_healthcare.clients import omop_client

        respx.get("https://athena.ohdsi.org/api/v1/concepts").respond(
            200, json={"content": [{"conceptId": 1, "conceptName": "Diabetes"}]},
        )
        result = await omop_client.search(server, "Diabetes")
        assert "content" in result


class TestREDCapRecords:
    async def test_redcap_requires_auth(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_healthcare.clients import redcap_client

        monkeypatch.delenv("REDCAP_API_TOKEN", raising=False)
        with pytest.raises(AuthenticationError) as exc_info:
            await redcap_client.records(server, "proj-1")
        assert "REDCAP_API_TOKEN" in exc_info.value.message

    @respx.mock
    async def test_redcap_records_with_token(self, server: BaseLifeSciencesServer, monkeypatch):
        from life_sciences_healthcare.clients import redcap_client

        monkeypatch.setenv("REDCAP_API_TOKEN", "test-token")
        respx.post("https://redcap.example.org/api/").respond(
            200, json=[{"record_id": "1", "field_1": "value"}],
        )
        result = await redcap_client.records(server, "proj-1")
        assert isinstance(result, list)


class TestDICOMwebQuery:
    @respx.mock
    async def test_dicomweb_query(self, server: BaseLifeSciencesServer):
        from life_sciences_healthcare.clients import dicomweb_client

        respx.get("https://dicomweb.example.org/dicom-web/studies").respond(
            200, json=[{"StudyInstanceUID": "1.2.3.4"}],
        )
        result = await dicomweb_client.query(server, patient_id="P001")
        assert isinstance(result, list)
