"""WDL pipeline registry client.

Indexes GATK best practices and community WDL pipelines.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "WDL Pipelines"
BASE_URL = "https://api.github.com/"

# Well-known WDL pipelines
_WDL_PIPELINES = [
    {
        "name": "gatk-germline-short-variant",
        "description": "GATK Best Practices: Germline Short Variant Discovery",
        "language": "WDL",
        "repository": "broadinstitute/gatk",
        "category": "variant-calling",
    },
    {
        "name": "gatk-somatic-short-variant",
        "description": "GATK Best Practices: Somatic Short Variant Discovery",
        "language": "WDL",
        "repository": "broadinstitute/gatk",
        "category": "variant-calling",
    },
    {
        "name": "gatk-germline-cnv",
        "description": "GATK Best Practices: Germline CNV Discovery",
        "language": "WDL",
        "repository": "broadinstitute/gatk",
        "category": "variant-calling",
    },
    {
        "name": "gatk-joint-genotyping",
        "description": "GATK Best Practices: Joint Genotyping",
        "language": "WDL",
        "repository": "broadinstitute/gatk",
        "category": "variant-calling",
    },
]


async def list_pipelines(
    server: BaseLifeSciencesServer,
    max_results: int = 20,
) -> dict[str, Any]:
    """List available WDL pipelines."""
    pipelines = _WDL_PIPELINES[:max_results]
    return {"pipelines": pipelines, "count": len(pipelines)}


async def get_pipeline(
    server: BaseLifeSciencesServer,
    name: str,
) -> dict[str, Any]:
    """Get details for a specific WDL pipeline."""
    for pipeline in _WDL_PIPELINES:
        if pipeline["name"].lower() == name.lower():
            return pipeline
    return {"error": f"Pipeline '{name}' not found", "name": name}
