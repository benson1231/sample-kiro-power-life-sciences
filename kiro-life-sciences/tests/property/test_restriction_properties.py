"""Property 14: Restriction Enzyme Fragment Size Invariant.

For any DNA sequence and enzyme set, the sum of fragment sizes must equal
the original sequence length.

**Validates: Requirements 29.2, 29.3**
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-restriction-prop")
    yield srv
    await srv.cleanup()


# Strategy: generate DNA sequences of varying lengths
_dna_st = st.text(
    alphabet="ACGT",
    min_size=1,
    max_size=500,
)

# Strategy: pick a subset of known enzymes
_enzyme_names = [
    "EcoRI", "BamHI", "HindIII", "XhoI", "NdeI",
    "NcoI", "SalI", "XbaI", "PstI", "SphI",
    "KpnI", "SacI", "NotI", "BglII", "ClaI",
    "EcoRV", "SmaI", "ApaI", "NheI", "SpeI",
]

_enzyme_subset_st = st.lists(
    st.sampled_from(_enzyme_names),
    min_size=1,
    max_size=10,
    unique=True,
)


class TestRestrictionFragmentSizeInvariant:
    """For any DNA sequence and enzyme set, the sum of fragment sizes
    equals the original sequence length.

    **Validates: Requirements 29.2, 29.3**
    """

    @given(sequence=_dna_st, enzymes=_enzyme_subset_st)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_fragment_sum_equals_sequence_length(
        self, sequence: str, enzymes: list[str], server: BaseLifeSciencesServer,
    ):
        from life_sciences_molbio.clients import restriction_client

        result = await restriction_client.analysis(server, sequence, enzymes)

        seq_len = result["sequence_length"]
        fragments = result["combined_fragments"]

        # If there are any cuts, fragments should sum to sequence length
        if fragments:
            assert sum(fragments) == seq_len, (
                f"Fragment sum {sum(fragments)} != sequence length {seq_len}"
            )
        # If no cuts, combined_fragments is empty — that's fine,
        # the whole sequence is one fragment of length seq_len

    @given(sequence=_dna_st, enzymes=_enzyme_subset_st)
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_all_fragments_non_negative(
        self, sequence: str, enzymes: list[str], server: BaseLifeSciencesServer,
    ):
        from life_sciences_molbio.clients import restriction_client

        result = await restriction_client.analysis(server, sequence, enzymes)
        fragments = result["combined_fragments"]

        for frag in fragments:
            assert frag >= 0, f"Fragment size must be non-negative, got {frag}"
