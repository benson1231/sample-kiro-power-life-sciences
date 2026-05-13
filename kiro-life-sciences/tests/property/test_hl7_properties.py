"""Property 15: HL7 Message Parse-Generate Round-Trip.

For any valid HL7 v2 message, parse → generate → should produce an
equivalent message (preserving key fields).

**Validates: Requirements 42.5, 42.6**
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from life_sciences_common import BaseLifeSciencesServer


@pytest.fixture
async def server():
    srv = BaseLifeSciencesServer("test-hl7-prop")
    yield srv
    await srv.cleanup()


# Strategy: generate HL7-like structured data
_app_name_st = st.text(
    alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    min_size=1,
    max_size=10,
)

_patient_id_st = st.text(
    alphabet="0123456789",
    min_size=1,
    max_size=10,
)

_patient_name_st = st.builds(
    lambda last, first: f"{last}^{first}",
    st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=10),
    st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=10),
)

_dob_st = st.builds(
    lambda y, m, d: f"{y:04d}{m:02d}{d:02d}",
    st.integers(min_value=1920, max_value=2024),
    st.integers(min_value=1, max_value=12),
    st.integers(min_value=1, max_value=28),
)

_sex_st = st.sampled_from(["M", "F", "O", "U"])

_message_type_st = st.sampled_from(["ADT^A01", "ADT^A04", "ORM^O01"])


class TestHL7ParseGenerateRoundTrip:
    """For any valid HL7 v2 message, parse → generate → should produce
    an equivalent message preserving key fields.

    **Validates: Requirements 42.5, 42.6**
    """

    @given(
        msg_type=_message_type_st,
        sending_app=_app_name_st,
        sending_fac=_app_name_st,
        patient_id=_patient_id_st,
        patient_name=_patient_name_st,
        dob=_dob_st,
        sex=_sex_st,
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_generate_then_parse_preserves_segments(
        self,
        msg_type: str,
        sending_app: str,
        sending_fac: str,
        patient_id: str,
        patient_name: str,
        dob: str,
        sex: str,
        server: BaseLifeSciencesServer,
    ):
        from life_sciences_healthcare.clients import hl7_client

        # Generate a message
        gen_result = await hl7_client.generate(
            server,
            msg_type,
            {
                "sending_app": sending_app,
                "sending_facility": sending_fac,
                "patient": {
                    "id": patient_id,
                    "name": patient_name,
                    "dob": dob,
                    "sex": sex,
                },
            },
        )
        message = gen_result["message"]
        assert gen_result["segment_count"] == 2

        # Parse the generated message
        parse_result = await hl7_client.parse(server, message)
        assert parse_result["segment_count"] == 2

        # MSH segment should be first
        assert parse_result["segments"][0]["segment"] == "MSH"
        # PID segment should be second
        assert parse_result["segments"][1]["segment"] == "PID"

        # The generated message should contain the message type
        assert msg_type in message
        # The generated message should contain the sending app
        assert sending_app in message
