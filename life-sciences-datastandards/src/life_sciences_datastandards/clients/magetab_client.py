"""MAGE-TAB (MicroArray Gene Expression Tabular) format client.

Provides validation and parsing of MAGE-TAB formatted data.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "MAGE-TAB"


async def validate(
    server: BaseLifeSciencesServer,
    content: str,
) -> dict[str, Any]:
    """Validate MAGE-TAB formatted content."""
    errors = []
    warnings = []
    lines = content.strip().split("\n")

    if not lines:
        errors.append("Empty MAGE-TAB content")
    else:
        has_idf = any(line.startswith("Investigation Title") for line in lines)
        if not has_idf:
            warnings.append("Missing 'Investigation Title' field")

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
    """Parse MAGE-TAB formatted content into structured data."""
    lines = content.strip().split("\n")
    fields: dict[str, str] = {}
    for line in lines:
        parts = line.split("\t", 1)
        if len(parts) == 2:
            fields[parts[0].strip()] = parts[1].strip()
    return {"fields": fields, "field_count": len(fields)}
