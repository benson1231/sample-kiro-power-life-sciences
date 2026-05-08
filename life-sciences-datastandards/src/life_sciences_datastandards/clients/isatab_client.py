"""ISA-Tab (Investigation/Study/Assay Tabular) format client.

Provides validation and parsing of ISA-Tab formatted data.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "ISA-Tab"


async def validate(
    server: BaseLifeSciencesServer,
    content: str,
) -> dict[str, Any]:
    """Validate ISA-Tab formatted content."""
    errors = []
    warnings = []
    lines = content.strip().split("\n")

    if not lines:
        errors.append("Empty ISA-Tab content")
    else:
        has_investigation = any("ONTOLOGY SOURCE REFERENCE" in line for line in lines)
        if not has_investigation:
            warnings.append("Missing ONTOLOGY SOURCE REFERENCE section")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "line_count": len(lines),
    }


async def parse(
    server: BaseLifeSciencesServer,
    content: str,
) -> dict[str, Any]:
    """Parse ISA-Tab formatted content into structured data."""
    lines = content.strip().split("\n")
    sections: dict[str, list[str]] = {}
    current_section = "header"
    for line in lines:
        if line.startswith("ONTOLOGY") or line.startswith("INVESTIGATION") or line.startswith("STUDY"):
            current_section = line.strip()
            sections[current_section] = []
        else:
            sections.setdefault(current_section, []).append(line)
    return {"sections": {k: len(v) for k, v in sections.items()}, "section_count": len(sections)}
