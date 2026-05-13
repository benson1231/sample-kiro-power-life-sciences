---
inclusion: auto
fileMatchPattern: "**/*dock*,**/*ligand*,**/*binding*"
---

# Molecular Docking

Step-by-step guide for protein-ligand docking using PDB structures and SwissDock.

## Step 1: Obtain Protein Structure

1. Search PDB for the target protein:
   - Use `life-sciences-structural` → `pdb_search` tool.
2. Select a structure with good resolution (< 2.5 Å) and relevant ligand.
3. Fetch the structure:
   - Use `life-sciences-structural` → `pdb_fetch` tool with PDB ID.

## Step 2: Prepare the Protein

1. Remove water molecules and non-essential heteroatoms.
2. Add hydrogen atoms and assign charges.
3. Define the binding site:
   - Use known ligand position from the crystal structure, or
   - Predict binding pockets from surface analysis.

## Step 3: Prepare Ligands

1. Get ligand SMILES from PubChem or draw in a molecular editor:
   - Use `life-sciences-cheminformatics` → `pubchem_search` tool.
2. Generate 3D conformers from SMILES.
3. Assign partial charges and minimize energy.

## Step 4: Run Docking

1. Submit docking job to SwissDock:
   - Use `life-sciences-cheminformatics` → `docking_submit` tool.
2. Provide protein structure, ligand, and binding site definition.
3. Wait for docking to complete (typically 5–30 minutes).

## Step 5: Analyze Docking Results

1. Retrieve docking poses and scores.
2. Rank poses by binding energy (more negative = stronger binding).
3. Inspect top poses for:
   - Hydrogen bonds with key residues.
   - Hydrophobic contacts in the binding pocket.
   - Steric clashes or unfavorable interactions.

## Step 6: Validate and Refine

1. Compare docking pose with known co-crystal structure (if available).
2. Calculate RMSD between docked and experimental pose (< 2.0 Å is good).
3. Run molecular dynamics simulation for pose refinement (optional).

## Expected Outputs
- Ranked docking poses with binding energies.
- Interaction analysis (H-bonds, hydrophobic contacts).
- Visualization of top binding poses.
