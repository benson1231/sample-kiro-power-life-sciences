"""Property 16: Data Standards Validation Round-Trip.

For any valid SBML model, serialize → parse → should produce an
equivalent model (species, reactions, compartments preserved).

**Validates: Requirements 51.5, 51.6, 51.7, 51.3, 51.4**
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st, assume, HealthCheck

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-datastandards-prop")
    yield srv
    await srv.cleanup()


# Strategy: generate valid SBML-like identifiers
_id_st = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz",
    min_size=2,
    max_size=8,
).map(lambda s: s.replace(" ", ""))

_compartment_ids_st = st.lists(
    _id_st, min_size=1, max_size=5, unique=True,
)

_species_ids_st = st.lists(
    _id_st, min_size=0, max_size=10, unique=True,
)

_reaction_ids_st = st.lists(
    _id_st, min_size=0, max_size=5, unique=True,
)


def _build_sbml(
    compartments: list[str],
    species: list[str],
    reactions: list[str],
) -> str:
    """Build a minimal SBML XML string from component IDs."""
    parts = ['<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" level="3" version="1">']
    parts.append('<model id="test_model">')

    if compartments:
        parts.append("<listOfCompartments>")
        for c in compartments:
            parts.append(f'<compartment id="{c}" constant="true"/>')
        parts.append("</listOfCompartments>")

    if species:
        parts.append("<listOfSpecies>")
        comp = compartments[0] if compartments else "default"
        for s in species:
            parts.append(f'<species id="{s}" compartment="{comp}" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/>')
        parts.append("</listOfSpecies>")

    if reactions:
        parts.append("<listOfReactions>")
        for r in reactions:
            parts.append(f'<reaction id="{r}" reversible="false"/>')
        parts.append("</listOfReactions>")

    parts.append("</model></sbml>")
    return "\n".join(parts)


class TestSBMLValidationRoundTrip:
    """For any valid SBML model, validate → parse → should produce
    consistent results with the original model components.

    **Validates: Requirements 51.5, 51.6, 51.7, 51.3, 51.4**
    """

    @given(
        compartments=_compartment_ids_st,
        species=_species_ids_st,
        reactions=_reaction_ids_st,
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_sbml_validate_then_parse_preserves_components(
        self,
        compartments: list[str],
        species: list[str],
        reactions: list[str],
        server: BaseLifeSciencesServer,
    ):
        # Ensure no overlap between IDs
        all_ids = compartments + species + reactions
        assume(len(all_ids) == len(set(all_ids)))

        from life_sciences_datastandards.clients import sbml_client

        sbml_content = _build_sbml(compartments, species, reactions)

        # Validate
        val_result = await sbml_client.validate(server, sbml_content)
        assert val_result["valid"] is True

        # Parse
        parse_result = await sbml_client.parse(server, sbml_content)
        assert parse_result["species_count"] == len(species)
        assert parse_result["reaction_count"] == len(reactions)
        assert set(parse_result["compartments"]) == set(compartments)
        assert set(parse_result["species"]) == set(species)
        assert set(parse_result["reactions"]) == set(reactions)
