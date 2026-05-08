"""RDKit molecular descriptor and substructure search client.

Provides local computation of molecular descriptors and substructure
matching using SMILES/SMARTS notation.
"""

from __future__ import annotations

import re
from typing import Any

from life_sciences_common import BaseLifeSciencesServer

SERVICE_NAME = "RDKit"


def _count_atoms(smiles: str) -> dict[str, int]:
    """Simple atom counting from SMILES (heuristic)."""
    # Remove ring numbers, charges, and stereochemistry
    clean = re.sub(r"[\[\]@+\-\d#=/\\().]", " ", smiles)
    atoms: dict[str, int] = {}
    for token in clean.split():
        if token:
            atoms[token] = atoms.get(token, 0) + 1
    return atoms


async def descriptors(
    server: BaseLifeSciencesServer,
    smiles: str,
) -> dict[str, Any]:
    """Compute molecular descriptors from a SMILES string."""
    # Basic heuristic descriptors (real implementation would use RDKit library)
    heavy_atoms = sum(1 for c in smiles if c.isalpha() and c.isupper())
    rings = smiles.count("1") // 2 + smiles.count("2") // 2
    rotatable = smiles.count("-") + max(0, smiles.count("C") - 1 - rings * 2)
    hbd = smiles.count("N") + smiles.count("O")  # rough estimate
    hba = smiles.count("N") + smiles.count("O") + smiles.count("F")

    return {
        "smiles": smiles,
        "heavy_atom_count": heavy_atoms,
        "ring_count": rings,
        "estimated_rotatable_bonds": max(0, rotatable),
        "estimated_hbd": hbd,
        "estimated_hba": hba,
        "atom_counts": _count_atoms(smiles),
        "note": "These are heuristic estimates. For precise values, use RDKit library directly.",
    }


async def substructure(
    server: BaseLifeSciencesServer,
    smarts: str,
    molecules: list[str],
) -> dict[str, Any]:
    """Check which molecules contain a SMARTS substructure pattern."""
    # Simple substring-based matching (real implementation would use RDKit)
    # Convert SMARTS to a simplified pattern for basic matching
    matches = []
    non_matches = []
    for mol in molecules:
        # Basic heuristic: check if key atoms from SMARTS appear in SMILES
        smarts_atoms = set(re.findall(r"[A-Z][a-z]?", smarts))
        mol_atoms = set(re.findall(r"[A-Z][a-z]?", mol))
        if smarts_atoms.issubset(mol_atoms):
            matches.append(mol)
        else:
            non_matches.append(mol)

    return {
        "smarts_pattern": smarts,
        "total_molecules": len(molecules),
        "matches": matches,
        "match_count": len(matches),
        "non_matches": non_matches,
        "note": "Heuristic matching. For precise substructure search, use RDKit library directly.",
    }
