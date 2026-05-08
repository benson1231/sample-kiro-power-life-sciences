"""CWL pipeline registry client.

Indexes CWL community and Seven Bridges pipelines.
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "CWL Pipelines"

# Well-known CWL pipelines
_CWL_PIPELINES = [
    {
        "name": "cwl-rnaseq",
        "description": "CWL RNA-Seq analysis pipeline",
        "language": "CWL",
        "repository": "common-workflow-language/workflows",
        "category": "rna-seq",
    },
    {
        "name": "cwl-variant-calling",
        "description": "CWL variant calling pipeline",
        "language": "CWL",
        "repository": "common-workflow-language/workflows",
        "category": "variant-calling",
    },
    {
        "name": "sb-whole-genome",
        "description": "Seven Bridges Whole Genome Sequencing pipeline",
        "language": "CWL",
        "repository": "sevenbridges-openworkflows/Whole-Genome-Sequencing",
        "category": "whole-genome",
    },
    {
        "name": "sb-rna-seq",
        "description": "Seven Bridges RNA-Seq Quantification pipeline",
        "language": "CWL",
        "repository": "sevenbridges-openworkflows/RNA-seq-quantification",
        "category": "rna-seq",
    },
]


async def list_pipelines(
    server: BaseLifeSciencesServer,
    max_results: int = 20,
) -> dict[str, Any]:
    """List available CWL pipelines."""
    pipelines = _CWL_PIPELINES[:max_results]
    return {"pipelines": pipelines, "count": len(pipelines)}


async def get_pipeline(
    server: BaseLifeSciencesServer,
    name: str,
) -> dict[str, Any]:
    """Get details for a specific CWL pipeline."""
    for pipeline in _CWL_PIPELINES:
        if pipeline["name"].lower() == name.lower():
            return pipeline
    return {"error": f"Pipeline '{name}' not found", "name": name}
