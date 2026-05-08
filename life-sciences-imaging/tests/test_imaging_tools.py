"""Unit tests for life-sciences-imaging MCP server tools.

Uses ``respx`` to mock httpx responses following the genomics test pattern.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-imaging")
    yield srv
    await srv.cleanup()


class TestOMEROSearch:
    @respx.mock
    async def test_omero_search(self, server: BaseLifeSciencesServer):
        from life_sciences_imaging.clients import omero_client

        respx.get("https://idr.openmicroscopy.org/api/v0/m/images/").respond(
            200, json={"data": [{"id": 1, "name": "cell_image.tif"}]},
        )
        result = await omero_client.search(server, "cell")
        assert "data" in result


class TestDICOMQuery:
    @respx.mock
    async def test_dicom_query(self, server: BaseLifeSciencesServer):
        from life_sciences_imaging.clients import dicom_client

        respx.get("https://dicomweb.example.org/dicom-web/studies").respond(
            200, json=[{"StudyInstanceUID": "1.2.3.4"}],
        )
        result = await dicom_client.query(server, patient_id="P001")
        assert isinstance(result, list)


class TestBioImageSearch:
    @respx.mock
    async def test_bioimage_search(self, server: BaseLifeSciencesServer):
        from life_sciences_imaging.clients import bioimage_client

        respx.get("https://www.ebi.ac.uk/bioimage-archive/api/v1/images/search").respond(
            200, json={"images": [{"accession": "S-BIAD1"}]},
        )
        result = await bioimage_client.search(server, "fluorescence")
        assert "images" in result


class TestIDRSearch:
    @respx.mock
    async def test_idr_search(self, server: BaseLifeSciencesServer):
        from life_sciences_imaging.clients import idr_client

        respx.get("https://idr.openmicroscopy.org/api/v0/m/screens/").respond(
            200, json={"data": [{"id": 1, "name": "idr0001"}]},
        )
        result = await idr_client.search(server, "screen")
        assert "data" in result


class TestEMPIARSearch:
    @respx.mock
    async def test_empiar_search(self, server: BaseLifeSciencesServer):
        from life_sciences_imaging.clients import empiar_client

        respx.get("https://www.ebi.ac.uk/empiar/api/entry/search").respond(
            200, json={"entries": [{"empiar_id": "EMPIAR-10028"}]},
        )
        result = await empiar_client.search(server, "ribosome")
        assert "entries" in result
