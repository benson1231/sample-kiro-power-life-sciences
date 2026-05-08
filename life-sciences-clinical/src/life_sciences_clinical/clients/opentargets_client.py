"""Open Targets Platform API client.

GraphQL endpoint: https://api.platform.opentargets.org/api/v4/graphql
"""

from __future__ import annotations

import json
from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "OpenTargets"
BASE_URL = "https://api.platform.opentargets.org/api/v4/graphql"

_JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


async def search(
    server: BaseLifeSciencesServer,
    query: str,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search Open Targets for targets or diseases."""
    graphql_query = {
        "query": """
            query SearchQuery($queryString: String!, $size: Int!) {
                search(queryString: $queryString, page: {size: $size, index: 0}) {
                    total
                    hits {
                        id
                        name
                        entity
                        description
                    }
                }
            }
        """,
        "variables": {"queryString": query, "size": max_results},
    }
    response = await server._request_with_retry(
        "POST",
        BASE_URL,
        headers=_JSON_HEADERS,
        content=json.dumps(graphql_query),
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()
