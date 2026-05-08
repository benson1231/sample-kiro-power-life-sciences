"""SBML (Systems Biology Markup Language) format client.

Provides validation and parsing of SBML formatted data.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "SBML"


async def validate(
    server: BaseLifeSciencesServer,
    content: str,
) -> dict[str, Any]:
    """Validate SBML formatted content."""
    errors = []
    warnings = []

    if not content.strip():
        errors.append("Empty SBML content")
    elif "<sbml" not in content.lower():
        errors.append("Missing <sbml> root element")
    else:
        if "<model" not in content.lower():
            warnings.append("Missing <model> element")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


async def parse(
    server: BaseLifeSciencesServer,
    content: str,
) -> dict[str, Any]:
    """Parse SBML formatted content into structured data."""
    # Basic XML tag extraction
    import re
    species = re.findall(r'<species\s+[^>]*id="([^"]*)"', content)
    reactions = re.findall(r'<reaction\s+[^>]*id="([^"]*)"', content)
    compartments = re.findall(r'<compartment\s+[^>]*id="([^"]*)"', content)
    return {
        "species": species,
        "reactions": reactions,
        "compartments": compartments,
        "species_count": len(species),
        "reaction_count": len(reactions),
    }
