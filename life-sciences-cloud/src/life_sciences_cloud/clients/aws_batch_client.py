"""AWS Batch API client.

Base URL: https://batch.us-east-1.amazonaws.com/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "AWS Batch"
BASE_URL = "https://batch.us-east-1.amazonaws.com/"


async def submit(
    server: BaseLifeSciencesServer,
    job_definition: str,
    queue: str,
    parameters: dict[str, Any],
) -> dict[str, Any]:
    """Submit a job to AWS Batch."""
    url = f"{BASE_URL}v1/submitjob"
    payload = {
        "jobDefinition": job_definition,
        "jobQueue": queue,
        "parameters": parameters,
    }
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=job_definition)
    return response.json()


async def status(
    server: BaseLifeSciencesServer,
    job_id: str,
) -> dict[str, Any]:
    """Get the status of an AWS Batch job."""
    url = f"{BASE_URL}v1/describejobs"
    payload = {"jobs": [job_id]}
    response = await server._request_with_retry("POST", url, json=payload)
    await server._handle_api_error(response, SERVICE_NAME, query=job_id)
    return response.json()
