"""Unit tests for life-sciences-proteomics MCP server tools.

Uses ``respx`` to mock httpx responses, following the same pattern as
``life-sciences-common/tests/test_server.py``.
"""

from __future__ import annotations

import pytest
import respx

from life_sciences_common import BaseLifeSciencesServer


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-proteomics")
    yield srv
    await srv.cleanup()


# ---------------------------------------------------------------------------
# UniProt tools
# ---------------------------------------------------------------------------


class TestUniProtTools:
    @respx.mock
    async def test_uniprot_search(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import uniprot_client

        respx.get("https://rest.uniprot.org/uniprotkb/search").respond(
            200,
            json={
                "results": [
                    {
                        "primaryAccession": "P04637",
                        "uniProtkbId": "P53_HUMAN",
                        "organism": {"scientificName": "Homo sapiens"},
                    }
                ]
            },
        )
        result = await uniprot_client.search(server, "TP53", 10)
        assert "results" in result
        assert result["results"][0]["primaryAccession"] == "P04637"

    @respx.mock
    async def test_uniprot_fetch(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import uniprot_client

        respx.get("https://rest.uniprot.org/uniprotkb/P04637.json").respond(
            200,
            json={
                "primaryAccession": "P04637",
                "proteinDescription": {
                    "recommendedName": {"fullName": {"value": "Cellular tumor antigen p53"}}
                },
            },
        )
        result = await uniprot_client.fetch(server, "P04637")
        assert result["primaryAccession"] == "P04637"

    @respx.mock
    async def test_uniprot_sequence(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import uniprot_client

        fasta = ">sp|P04637|P53_HUMAN Cellular tumor antigen p53\nMEEPQSDPSVEPPLSQETFS\n"
        respx.get("https://rest.uniprot.org/uniprotkb/P04637.fasta").respond(
            200, text=fasta,
        )
        result = await uniprot_client.sequence(server, "P04637")
        assert result["accession"] == "P04637"
        assert result["format"] == "fasta"
        assert "P53_HUMAN" in result["data"]


# ---------------------------------------------------------------------------
# InterPro tools
# ---------------------------------------------------------------------------


class TestInterProTools:
    @respx.mock
    async def test_interpro_lookup_by_domain(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import interpro_client

        respx.get(
            "https://www.ebi.ac.uk/interpro/api/entry/interpro/IPR011364"
        ).respond(
            200,
            json={
                "metadata": {
                    "accession": "IPR011364",
                    "name": "BRCA1",
                    "type": "family",
                }
            },
        )
        result = await interpro_client.lookup(server, "IPR011364")
        assert result["metadata"]["accession"] == "IPR011364"

    @respx.mock
    async def test_interpro_lookup_by_protein(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import interpro_client

        respx.get(
            "https://www.ebi.ac.uk/interpro/api/protein/uniprot/P04637"
        ).respond(
            200,
            json={"metadata": {"accession": "P04637", "name": "P53_HUMAN"}},
        )
        result = await interpro_client.lookup(server, "P04637")
        assert result["metadata"]["accession"] == "P04637"


# ---------------------------------------------------------------------------
# Pfam tools
# ---------------------------------------------------------------------------


class TestPfamTools:
    @respx.mock
    async def test_pfam_family(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import pfam_client

        respx.get(
            "https://www.ebi.ac.uk/interpro/api/entry/pfam/PF00069"
        ).respond(
            200,
            json={
                "metadata": {
                    "accession": "PF00069",
                    "name": "Pkinase",
                    "type": "family",
                }
            },
        )
        result = await pfam_client.family(server, "PF00069")
        assert result["metadata"]["accession"] == "PF00069"
        assert result["metadata"]["name"] == "Pkinase"


# ---------------------------------------------------------------------------
# STRING tools
# ---------------------------------------------------------------------------


class TestSTRINGTools:
    @respx.mock
    async def test_string_interactions(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import string_client

        respx.get("https://string-db.org/api/json/network").respond(
            200,
            json=[
                {
                    "stringId_A": "9606.ENSP00000269305",
                    "stringId_B": "9606.ENSP00000418960",
                    "preferredName_A": "TP53",
                    "preferredName_B": "MDM2",
                    "score": 0.999,
                }
            ],
        )
        result = await string_client.interactions(server, "TP53", species=9606)
        assert result["protein"] == "TP53"
        assert result["species"] == 9606
        assert len(result["interactions"]) == 1
        assert result["interactions"][0]["preferredName_A"] == "TP53"


# ---------------------------------------------------------------------------
# PRIDE tools
# ---------------------------------------------------------------------------


class TestPRIDETools:
    @respx.mock
    async def test_pride_search(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import pride_client

        respx.get(
            "https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects"
        ).respond(
            200,
            json={
                "_embedded": {
                    "compactprojects": [
                        {"accession": "PXD000001", "title": "Proteome of HeLa cells"}
                    ]
                },
                "page": {"totalElements": 1},
            },
        )
        result = await pride_client.search(server, "HeLa", 10)
        assert "page" in result or "_embedded" in result


# ---------------------------------------------------------------------------
# neXtProt tools
# ---------------------------------------------------------------------------


class TestNeXtProtTools:
    @respx.mock
    async def test_nextprot_entry(self, server: BaseLifeSciencesServer):
        from life_sciences_proteomics.clients import nextprot_client

        respx.get("https://api.nextprot.org/entry/NX_TP53.json").respond(
            200,
            json={
                "entry": {
                    "uniqueName": "NX_TP53",
                    "overview": {"proteinNames": [{"name": "Cellular tumor antigen p53"}]},
                }
            },
        )
        result = await nextprot_client.entry(server, "TP53")
        assert result["entry"]["uniqueName"] == "NX_TP53"
