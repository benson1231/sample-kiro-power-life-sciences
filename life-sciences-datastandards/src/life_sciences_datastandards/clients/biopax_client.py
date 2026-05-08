"""BioPAX (Biological Pathway Exchange) format client.

Provides parsing of BioPAX formatted data.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "BioPAX"


async def parse(
    server: BaseLifeSciencesServer,
    content: str,
) -> dict[str, Any]:
    """Parse BioPAX formatted content into structured data."""
    import re
    pathways = re.findall(r'<bp:Pathway\s+[^>]*rdf:ID="([^"]*)"', content)
    proteins = re.findall(r'<bp:Protein\s+[^>]*rdf:ID="([^"]*)"', content)
    interactions = re.findall(r'<bp:Interaction\s+[^>]*rdf:ID="([^"]*)"', content)
    return {
        "pathways": pathways,
        "proteins": proteins,
        "interactions": interactions,
        "pathway_count": len(pathways),
        "protein_count": len(proteins),
        "interaction_count": len(interactions),
    }
