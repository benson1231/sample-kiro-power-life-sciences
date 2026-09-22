"""cBioPortal API client.

Base URL: https://www.cbioportal.org/api

cBioPortal is an open-access resource for interactive exploration of
multidimensional cancer genomics data sets. No authentication is required.
"""

from __future__ import annotations

import re
import statistics
from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "cBioPortal"
BASE_URL = "https://www.cbioportal.org/api"

_JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

_VALID_STUDY_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_study_id(study_id: str) -> str:
    """Validate a study identifier before interpolating it into a URL path.

    Only letters, digits, underscores, and hyphens are allowed. Raises
    :class:`ValueError` for anything else to guard against path injection.
    """
    if not _VALID_STUDY_ID_PATTERN.match(study_id):
        raise ValueError(
            f"Invalid study_id: {study_id!r}. "
            "Only letters, digits, underscores, and hyphens are allowed."
        )
    return study_id


async def _get(
    server: BaseLifeSciencesServer,
    path: str,
    params: dict[str, Any] | None = None,
    *,
    query: str = "",
) -> Any:
    """Issue a GET against the cBioPortal API and return the parsed JSON."""
    url = f"{BASE_URL}{path}"
    response = await server._request_with_retry(
        "GET", url, params=params, headers=_JSON_HEADERS,
    )
    await server._handle_api_error(response, SERVICE_NAME, query=query)
    return response.json()


async def search_studies(
    server: BaseLifeSciencesServer,
    keyword: str,
) -> dict[str, Any]:
    """Search cancer genomics studies by keyword.

    The cBioPortal ``/studies`` endpoint lists all studies; filtering is
    performed client-side on study id, name, and description (case-insensitive
    substring match).
    """
    studies = await _get(server, "/studies", query=keyword)
    needle = keyword.lower()
    results = []
    for s in studies:
        haystack = " ".join(
            str(s.get(field, ""))
            for field in ("studyId", "name", "description")
        ).lower()
        if needle and needle not in haystack:
            continue
        results.append(
            {
                "study_id": s.get("studyId", ""),
                "name": s.get("name", ""),
                "samples": s.get("allSampleCount", 0),
                "description": s.get("description", "")[:300],
                "citation": s.get("citation", ""),
                "genome": s.get("referenceGenome", ""),
            }
        )
    total_samples = sum(r["samples"] for r in results)
    summary = (
        f"Found {len(results)} studies matching '{keyword}' "
        f"({total_samples} total samples)"
    )
    return {"summary": summary, "studies": results}


async def get_study_details(
    server: BaseLifeSciencesServer,
    study_id: str,
) -> dict[str, Any]:
    """Get detailed information about a study including molecular profiles and sample lists."""
    study_id = _validate_study_id(study_id)
    study = await _get(server, f"/studies/{study_id}", query=study_id)
    profiles = await _get(
        server, f"/studies/{study_id}/molecular-profiles", query=study_id,
    )
    sample_lists = await _get(
        server, f"/studies/{study_id}/sample-lists", query=study_id,
    )
    return {
        "study": study,
        "molecular_profiles": [
            {
                "id": p.get("molecularProfileId"),
                "name": p.get("name"),
                "type": p.get("molecularAlterationType"),
            }
            for p in profiles
        ],
        "sample_lists": [
            {
                "id": sl.get("sampleListId"),
                "name": sl.get("name"),
                "description": sl.get("description", ""),
            }
            for sl in sample_lists
        ],
    }


async def get_molecular_profiles(
    server: BaseLifeSciencesServer,
    study_id: str,
) -> list[dict[str, Any]]:
    """List available molecular data types for a study.

    Covers mutations, copy number, expression, methylation, and more.
    """
    study_id = _validate_study_id(study_id)
    profiles = await _get(
        server, f"/studies/{study_id}/molecular-profiles", query=study_id,
    )
    return [
        {
            "id": p.get("molecularProfileId"),
            "name": p.get("name"),
            "type": p.get("molecularAlterationType"),
            "datatype": p.get("datatype"),
        }
        for p in profiles
    ]


async def get_clinical_data(
    server: BaseLifeSciencesServer,
    study_id: str,
    attribute_id: str = "",
    data_type: str = "SAMPLE",
) -> dict[str, Any]:
    """Get clinical data for samples in a study.

    Omit ``attribute_id`` to list the available clinical attributes for the
    study instead of fetching values.
    """
    study_id = _validate_study_id(study_id)
    if not attribute_id:
        attrs = await _get(
            server, f"/studies/{study_id}/clinical-attributes", query=study_id,
        )
        return {
            "available_attributes": [
                {
                    "id": a.get("clinicalAttributeId"),
                    "name": a.get("displayName"),
                    "datatype": a.get("datatype"),
                }
                for a in attrs
            ]
        }
    data = await _get(
        server,
        f"/studies/{study_id}/clinical-data",
        {
            "clinicalDataType": data_type,
            "attributeId": attribute_id,
            "projection": "SUMMARY",
            "pageSize": 500,
        },
        query=attribute_id,
    )
    return {
        "study_id": study_id,
        "attribute_id": attribute_id,
        "data_type": data_type,
        "data": data[:200],
    }


async def search_genes(
    server: BaseLifeSciencesServer,
    keyword: str,
) -> list[dict[str, Any]]:
    """Search for gene information by symbol or alias.

    Returns Entrez gene ID, Hugo symbol, and gene type.
    """
    genes = await _get(server, "/genes", {"keyword": keyword}, query=keyword)
    return genes[:20]


async def compare_mutation_burden(
    server: BaseLifeSciencesServer,
    study_id: str,
) -> dict[str, Any]:
    """Compare tumor mutation burden (TMB) across samples in a study.

    High-TMB tumors generate more neoantigens and are better candidates for
    personalized cancer vaccines.
    """
    study_id = _validate_study_id(study_id)
    data = await _get(
        server,
        f"/studies/{study_id}/clinical-data",
        {
            "clinicalDataType": "SAMPLE",
            "attributeId": "MUTATION_COUNT",
            "projection": "SUMMARY",
            "pageSize": 1000,
        },
        query=study_id,
    )
    counts = [
        int(d["value"])
        for d in data
        if str(d.get("value", "")).isdigit()
    ]
    if not counts:
        return {
            "study_id": study_id,
            "error_message": "No mutation count data available for this study.",
        }
    counts.sort(reverse=True)
    return {
        "study_id": study_id,
        "samples_with_tmb_data": len(counts),
        "median_mutations": statistics.median(counts),
        "mean_mutations": round(statistics.mean(counts), 1),
        "max_mutations": max(counts),
        "min_mutations": min(counts),
        "high_tmb_above_100": sum(1 for c in counts if c > 100),
        "distribution": {
            "0-50": sum(1 for c in counts if c <= 50),
            "51-100": sum(1 for c in counts if 51 <= c <= 100),
            "101-500": sum(1 for c in counts if 101 <= c <= 500),
            "501-1000": sum(1 for c in counts if 501 <= c <= 1000),
            "1000+": sum(1 for c in counts if c > 1000),
        },
        "note": (
            "High TMB (>100 mutations) tumors generate more neoantigens — "
            "better candidates for personalized cancer vaccines."
        ),
    }


async def list_cancer_types(
    server: BaseLifeSciencesServer,
) -> list[dict[str, Any]]:
    """List all cancer types available in cBioPortal."""
    types = await _get(server, "/cancer-types")
    return [
        {
            "id": t.get("cancerTypeId"),
            "name": t.get("name"),
            "parent": t.get("parent", ""),
        }
        for t in types
    ]
