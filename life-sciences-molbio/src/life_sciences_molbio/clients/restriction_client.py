"""Restriction enzyme analysis client.

Provides local restriction site analysis and cloning design.
"""

from __future__ import annotations

import re
from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "Restriction Analysis"

# Common restriction enzyme recognition sites
_ENZYME_SITES: dict[str, str] = {
    "EcoRI": "GAATTC",
    "BamHI": "GGATCC",
    "HindIII": "AAGCTT",
    "XhoI": "CTCGAG",
    "NdeI": "CATATG",
    "NcoI": "CCATGG",
    "SalI": "GTCGAC",
    "XbaI": "TCTAGA",
    "PstI": "CTGCAG",
    "SphI": "GCATGC",
    "KpnI": "GGTACC",
    "SacI": "GAGCTC",
    "NotI": "GCGGCCGC",
    "BglII": "AGATCT",
    "ClaI": "ATCGAT",
    "EcoRV": "GATATC",
    "SmaI": "CCCGGG",
    "ApaI": "GGGCCC",
    "NheI": "GCTAGC",
    "SpeI": "ACTAGT",
}


async def analysis(
    server: BaseLifeSciencesServer,
    sequence: str,
    enzymes: list[str] | None = None,
) -> dict[str, Any]:
    """Find restriction enzyme cut sites in a DNA sequence."""
    seq_upper = sequence.upper().replace(" ", "").replace("\n", "")
    target_enzymes = enzymes if enzymes else list(_ENZYME_SITES.keys())

    results: list[dict[str, Any]] = []
    for enzyme_name in target_enzymes:
        site = _ENZYME_SITES.get(enzyme_name)
        if site is None:
            results.append({"enzyme": enzyme_name, "error": "Unknown enzyme"})
            continue
        positions = [m.start() for m in re.finditer(site, seq_upper)]
        results.append({
            "enzyme": enzyme_name,
            "recognition_site": site,
            "cut_positions": positions,
            "num_cuts": len(positions),
        })

    # Compute fragment sizes
    all_cuts = sorted(
        {pos for r in results if "cut_positions" in r for pos in r["cut_positions"]}
    )
    fragments = []
    if all_cuts:
        prev = 0
        for cut in all_cuts:
            fragments.append(cut - prev)
            prev = cut
        fragments.append(len(seq_upper) - prev)

    return {
        "sequence_length": len(seq_upper),
        "enzymes_analyzed": len(target_enzymes),
        "results": results,
        "combined_fragments": fragments,
    }


async def cloning_design(
    server: BaseLifeSciencesServer,
    vector: str,
    insert: str,
    sites: list[str],
) -> dict[str, Any]:
    """Design a cloning strategy with specified restriction sites."""
    vector_upper = vector.upper().replace(" ", "").replace("\n", "")
    insert_upper = insert.upper().replace(" ", "").replace("\n", "")

    site_info = []
    for site_name in sites:
        recognition = _ENZYME_SITES.get(site_name)
        if recognition is None:
            site_info.append({"enzyme": site_name, "error": "Unknown enzyme"})
            continue
        vector_positions = [m.start() for m in re.finditer(recognition, vector_upper)]
        insert_positions = [m.start() for m in re.finditer(recognition, insert_upper)]
        site_info.append({
            "enzyme": site_name,
            "recognition_site": recognition,
            "vector_positions": vector_positions,
            "insert_positions": insert_positions,
            "compatible": len(vector_positions) > 0 and len(insert_positions) == 0,
        })

    return {
        "vector_length": len(vector_upper),
        "insert_length": len(insert_upper),
        "restriction_sites": site_info,
        "strategy": "Clone insert into vector using specified restriction sites.",
    }
