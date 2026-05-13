---
inclusion: auto
fileMatchPattern: "**/*compound*,**/*screen*,**/*smiles*,**/*drug*"
---

# Compound Screening

Step-by-step guide using PubChem, RDKit, and ZINC for virtual compound screening.

## Step 1: Search PubChem for Compounds

1. Search PubChem by compound name or target:
   - Use `life-sciences-cheminformatics` → `pubchem_search` tool.
2. Retrieve compound properties: molecular weight, LogP, TPSA, SMILES.
3. Get bioactivity data for compounds with known target activity.

## Step 2: Calculate Molecular Descriptors

1. For each compound, calculate RDKit descriptors:
   - Use `life-sciences-cheminformatics` → `rdkit_descriptors` tool with SMILES.
2. Check Lipinski's Rule of Five compliance:
   - MW ≤ 500, LogP ≤ 5, HBD ≤ 5, HBA ≤ 10.
3. Calculate additional drug-likeness properties (TPSA, rotatable bonds).

## Step 3: Filter with ZINC Database

1. Search ZINC for purchasable analogs:
   - Use `life-sciences-cheminformatics` → `zinc_search` tool.
2. Filter by drug-likeness, availability, and price.
3. Select diverse compounds for screening library.

## Step 4: ADMET Prediction

1. Predict ADMET properties for selected compounds:
   - Use `life-sciences-cheminformatics` → `admet_predict` tool.
2. Filter out compounds with poor absorption, high toxicity, or CYP inhibition.
3. Check for PAINS (Pan-Assay Interference Compounds) alerts.

## Step 5: Molecular Docking (Optional)

1. Prepare the protein target structure from PDB.
2. Dock selected compounds:
   - Use `life-sciences-cheminformatics` → `docking_submit` tool.
3. Rank compounds by binding energy.
4. Visually inspect top poses for binding mode analysis.

## Expected Outputs
- Curated compound library with molecular properties.
- Lipinski and ADMET compliance report.
- Docking scores and binding poses for top candidates.
- Purchasable compound list from ZINC.
