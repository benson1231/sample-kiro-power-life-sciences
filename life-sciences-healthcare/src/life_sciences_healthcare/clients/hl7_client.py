"""HL7 v2 message parsing and generation client.

Provides local parsing and generation of HL7 v2 messages.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "HL7 v2"


async def parse(
    server: BaseLifeSciencesServer,
    message: str,
) -> dict[str, Any]:
    """Parse an HL7 v2 message into structured segments."""
    segments = message.strip().split("\r")
    if not segments:
        segments = message.strip().split("\n")

    parsed_segments = []
    for segment in segments:
        fields = segment.split("|")
        segment_name = fields[0] if fields else ""
        parsed_segments.append({
            "segment": segment_name,
            "fields": fields[1:] if len(fields) > 1 else [],
        })

    return {
        "message_type": parsed_segments[0]["fields"][8] if parsed_segments and len(parsed_segments[0].get("fields", [])) > 8 else "UNKNOWN",
        "segments": parsed_segments,
        "segment_count": len(parsed_segments),
    }


async def generate(
    server: BaseLifeSciencesServer,
    message_type: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Generate an HL7 v2 message from structured data."""
    msh = f"MSH|^~\\&|{data.get('sending_app', 'APP')}|{data.get('sending_facility', 'FAC')}|{data.get('receiving_app', 'APP')}|{data.get('receiving_facility', 'FAC')}|||{message_type}||P|2.5"
    segments = [msh]

    if "patient" in data:
        patient = data["patient"]
        pid = f"PID|||{patient.get('id', '')}||{patient.get('name', '')}||{patient.get('dob', '')}|{patient.get('sex', '')}"
        segments.append(pid)

    message = "\r".join(segments)
    return {"message": message, "segment_count": len(segments)}
