"""Unit tests for life-sciences-datastandards MCP server tools.

Tests local parsing/validation logic (no HTTP mocking needed for most).
"""

from __future__ import annotations

import pytest

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-datastandards")
    yield srv
    await srv.cleanup()


class TestMAGETABValidate:
    async def test_magetab_validate_valid(self, server: BaseLifeSciencesServer):
        from life_sciences_datastandards.clients import magetab_client

        content = "Investigation Title\tMy Experiment\nExperimental Design\tcase-control"
        result = await magetab_client.validate(server, content)
        assert result["valid"] is True
        assert result["line_count"] == 2

    async def test_magetab_validate_missing_title(self, server: BaseLifeSciencesServer):
        from life_sciences_datastandards.clients import magetab_client

        content = "Experimental Design\tcase-control"
        result = await magetab_client.validate(server, content)
        assert result["valid"] is True  # no errors, just warnings
        assert len(result["warnings"]) >= 1


class TestISATABValidate:
    async def test_isatab_validate_valid(self, server: BaseLifeSciencesServer):
        from life_sciences_datastandards.clients import isatab_client

        content = "ONTOLOGY SOURCE REFERENCE\nTerm Source Name\tOBI"
        result = await isatab_client.validate(server, content)
        assert result["valid"] is True

    async def test_isatab_validate_missing_section(self, server: BaseLifeSciencesServer):
        from life_sciences_datastandards.clients import isatab_client

        content = "Some random content"
        result = await isatab_client.validate(server, content)
        assert result["valid"] is True
        assert len(result["warnings"]) >= 1


class TestSBMLValidate:
    async def test_sbml_validate_valid(self, server: BaseLifeSciencesServer):
        from life_sciences_datastandards.clients import sbml_client

        content = '<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core"><model id="m1"></model></sbml>'
        result = await sbml_client.validate(server, content)
        assert result["valid"] is True

    async def test_sbml_validate_missing_root(self, server: BaseLifeSciencesServer):
        from life_sciences_datastandards.clients import sbml_client

        content = "<model>no sbml root</model>"
        result = await sbml_client.validate(server, content)
        assert result["valid"] is False
        assert any("sbml" in e.lower() for e in result["errors"])


class TestSBMLParse:
    async def test_sbml_parse(self, server: BaseLifeSciencesServer):
        from life_sciences_datastandards.clients import sbml_client

        content = '''<sbml><model id="m1">
            <listOfCompartments><compartment id="c1"/></listOfCompartments>
            <listOfSpecies><species id="s1"/><species id="s2"/></listOfSpecies>
            <listOfReactions><reaction id="r1"/></listOfReactions>
        </model></sbml>'''
        result = await sbml_client.parse(server, content)
        assert result["species_count"] == 2
        assert result["reaction_count"] == 1
        assert "c1" in result["compartments"]


class TestBioPAXParse:
    async def test_biopax_parse(self, server: BaseLifeSciencesServer):
        from life_sciences_datastandards.clients import biopax_client

        content = '''<rdf:RDF xmlns:bp="http://www.biopax.org/release/biopax-level3.owl#"
                              xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <bp:Pathway rdf:ID="pathway1"/>
            <bp:Protein rdf:ID="protein1"/>
        </rdf:RDF>'''
        result = await biopax_client.parse(server, content)
        assert result["pathway_count"] == 1
        assert result["protein_count"] == 1
