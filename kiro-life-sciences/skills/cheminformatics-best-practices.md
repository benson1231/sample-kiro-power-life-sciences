---
inclusion: manual
---

# Cheminformatics Best Practices

Practical guidance for molecular representations, property calculations, SAR analysis, and virtual screening.

## Molecular Representations

### SMILES (Simplified Molecular Input Line Entry System)
- Linear text notation for molecular structures.
- Atoms in brackets `[]`, bonds as `-`, `=`, `#`, `:`.
- Branching with `()`, rings with digit pairs.
- **Canonical SMILES**: Unique representation for a molecule (use RDKit `Chem.MolToSmiles`).

```python
from rdkit import Chem
mol = Chem.MolFromSmiles('CC(=O)Oc1ccccc1C(=O)O')  # Aspirin
canonical = Chem.MolToSmiles(mol)  # 'CC(=O)Oc1ccccc1C(=O)O'
```

### InChI (International Chemical Identifier)
- IUPAC standard for unique molecular identification.
- Layered structure: formula / connections / H atoms / charge / stereochemistry.
- Use **InChIKey** (27-character hash) for database lookups and deduplication.

### MOL / SDF Files (.mol, .sdf)
- 2D/3D coordinate-based format with atom and bond blocks.
- SDF files contain multiple molecules with associated data fields.
- Use for storing compound libraries with properties.

## Molecular Property Calculation

### Lipinski's Rule of Five
A compound is likely orally bioavailable if it satisfies:
- Molecular weight ≤ 500 Da
- LogP ≤ 5
- H-bond donors ≤ 5
- H-bond acceptors ≤ 10

```python
from rdkit.Chem import Descriptors
def check_lipinski(mol):
    return {
        'MW': Descriptors.MolWt(mol) <= 500,
        'LogP': Descriptors.MolLogP(mol) <= 5,
        'HBD': Descriptors.NumHDonors(mol) <= 5,
        'HBA': Descriptors.NumHAcceptors(mol) <= 10,
    }
```

### Key Descriptors
| Descriptor | Function | Typical Range |
|-----------|----------|---------------|
| Molecular Weight | `Descriptors.MolWt(mol)` | 100–500 Da |
| LogP | `Descriptors.MolLogP(mol)` | -2 to 5 |
| TPSA | `Descriptors.TPSA(mol)` | 20–140 Å² |
| Rotatable Bonds | `Descriptors.NumRotatableBonds(mol)` | 0–10 |
| Aromatic Rings | `Descriptors.NumAromaticRings(mol)` | 0–4 |

## Structure-Activity Relationship (SAR) Analysis

### Matched Molecular Pair Analysis
- Identify pairs of molecules differing by a single structural transformation.
- Correlate structural changes with activity changes.
- Use RDKit's `rdFMCS` for maximum common substructure detection.

### R-Group Decomposition
- Define a core scaffold and enumerate R-group substitutions.
- Analyze how each R-group position affects activity.
- Use `Chem.RGroupDecomposition` in RDKit.

### Activity Cliffs
- Pairs of structurally similar molecules with large activity differences.
- Identify using Tanimoto similarity > 0.8 and activity ratio > 10x.
- These highlight critical pharmacophoric features.

## Virtual Screening Workflows

### Ligand-Based Screening
1. Define active reference compounds.
2. Generate fingerprints (Morgan/ECFP4, MACCS, RDKit).
3. Calculate Tanimoto similarity to screen compound library.
4. Rank and filter by similarity threshold (typically > 0.4).

### Structure-Based Screening (Docking)
1. Prepare protein target (add hydrogens, remove water, define binding site).
2. Prepare ligand library (generate 3D conformers, assign charges).
3. Dock using AutoDock Vina, SwissDock, or Glide.
4. Score and rank by binding energy.
5. Visual inspection of top poses.

### ADMET Filtering
- Filter compounds early for drug-likeness (Lipinski, Veber rules).
- Predict ADMET properties: solubility, permeability, CYP inhibition, hERG liability.
- Remove PAINS (Pan-Assay Interference Compounds) using RDKit filters.

```python
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
params = FilterCatalogParams()
params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
catalog = FilterCatalog(params)
is_pains = catalog.HasMatch(mol)
```

## Database Integration
- **PubChem**: Search by name, SMILES, or InChI. Retrieve properties and bioassay data.
- **ChEMBL**: Query bioactivity data by target or compound.
- **ZINC**: Filter purchasable compounds by properties for virtual screening.
- Use the cheminformatics MCP server for programmatic access to all databases.
