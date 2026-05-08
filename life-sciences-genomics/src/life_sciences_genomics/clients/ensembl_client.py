"""Ensembl REST API client.

Base URL: https://rest.ensembl.org/
"""

from __future__ import annotations

from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Ensembl"
BASE_URL = "https://rest.ensembl.org/"

_JSON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


async def gene_lookup(
    server: BaseLifeSciencesServer,
    symbol: str,
    species: str = "homo_sapiens",
) -> dict[str, Any]:
    """Lookup a gene by symbol and species."""
    url = f"{BASE_URL}lookup/symbol/{species}/{symbol}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=symbol)
    return response.json()


async def variants(
    server: BaseLifeSciencesServer,
    region: str,
    species: str = "homo_sapiens",
) -> dict[str, Any]:
    """Get variants in a genomic region (e.g. '7:140424943-140624564')."""
    url = f"{BASE_URL}overlap/region/{species}/{region}"
    params = {"feature": "variation", "content-type": "application/json"}
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=region)
    return {"region": region, "species": species, "variants": response.json()}


async def sequence(
    server: BaseLifeSciencesServer,
    region: str,
    species: str = "homo_sapiens",
) -> dict[str, Any]:
    """Get nucleotide sequence for a genomic region."""
    url = f"{BASE_URL}sequence/region/{species}/{region}"
    response = await server._request_with_retry(
        "GET", url, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=region)
    return response.json()
