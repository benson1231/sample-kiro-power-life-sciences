"""GitHub community pipeline search client.

Base URL: https://api.github.com/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "GitHub Pipelines"
BASE_URL = "https://api.github.com/"


async def search_pipelines(
    server: BaseLifeSciencesServer,
    keyword: str,
    max_results: int = 20,
) -> dict[str, Any]:
    """Search GitHub for bioinformatics pipelines by keyword."""
    url = f"{BASE_URL}search/repositories"
    params: dict[str, Any] = {
        "q": f"{keyword} bioinformatics pipeline stars:>100",
        "sort": "stars",
        "order": "desc",
        "per_page": max_results,
    }
    response = await server._request_with_retry("GET", url, params=params)
    await server._handle_api_error(response, SERVICE_NAME, query=keyword)
    data = response.json()
    items = data.get("items", [])
    return {
        "keyword": keyword,
        "total_count": data.get("total_count", 0),
        "pipelines": [
            {
                "name": item.get("full_name", ""),
                "description": item.get("description", ""),
                "stars": item.get("stargazers_count", 0),
                "url": item.get("html_url", ""),
                "language": item.get("language", ""),
            }
            for item in items
        ],
    }


async def healthomics_import(
    server: BaseLifeSciencesServer,
    pipeline_name: str,
    workflow_language: str,
) -> dict[str, Any]:
    """Generate HealthOmics import instructions for a pipeline."""
    language_map = {
        "nextflow": "NEXTFLOW",
        "wdl": "WDL",
        "cwl": "CWL",
    }
    aho_language = language_map.get(workflow_language.lower(), workflow_language.upper())

    return {
        "pipeline": pipeline_name,
        "workflow_language": aho_language,
        "instructions": {
            "step_1": f"Clone the pipeline repository: git clone https://github.com/{pipeline_name}",
            "step_2": f"Package the workflow files into a ZIP archive",
            "step_3": f"Upload the ZIP to S3: aws s3 cp workflow.zip s3://your-bucket/workflows/",
            "step_4": f"Create the HealthOmics workflow using the CreateAHOWorkflow tool with workflow_type={aho_language}",
            "step_5": "Start a run using StartAHORun with appropriate parameters",
        },
        "notes": [
            f"Ensure all container images are available in ECR for HealthOmics access",
            f"Use CreateContainerRegistryMap to set up pull-through caches",
            f"Review the pipeline's parameter template before submitting runs",
        ],
    }
