---
inclusion: auto
fileMatchPattern: "**/*protein*,**/*structure*,**/*pdb*"
---

# Protein Structure Analysis

Step-by-step guide to search and analyze protein structures using PDB, AlphaFold, CATH, and UniProt.

## Step 1: Search for Experimental Structures

1. Search PDB by protein name or gene:
   - Use `life-sciences-structural` → `pdb_search` tool.
2. Review results: PDB ID, resolution, experimental method (X-ray, cryo-EM, NMR).
3. Select the best structure (lowest resolution for X-ray, highest confidence for cryo-EM).

## Step 2: Retrieve Structure Details

1. Fetch structure metadata by PDB ID:
   - Use `life-sciences-structural` → `pdb_fetch` tool.
2. Review chains, ligands, resolution, and deposition date.
3. Download structure file in PDB or mmCIF format if needed.

## Step 3: Check AlphaFold Predictions

1. If no experimental structure exists, query AlphaFold DB:
   - Use `life-sciences-structural` → `alphafold_query` tool with UniProt accession.
2. Review predicted structure confidence (pLDDT scores):
   - pLDDT > 90: Very high confidence.
   - pLDDT 70–90: Confident (backbone reliable).
   - pLDDT 50–70: Low confidence (use with caution).
   - pLDDT < 50: Very low confidence (likely disordered).
3. Check predicted aligned error (PAE) for domain-domain confidence.

## Step 4: Classify Protein Domains

1. Query CATH for domain classification:
   - Use `life-sciences-structural` → `cath_query` tool with PDB ID.
2. Review CATH classification: Class, Architecture, Topology, Homologous superfamily.
3. Identify functional domains and their structural context.

## Step 5: Retrieve UniProt Annotations

1. Fetch protein annotations from UniProt:
   - Use `life-sciences-proteomics` → `uniprot_fetch` tool with accession.
2. Review functional annotations, active sites, binding sites, and post-translational modifications.
3. Map structural features to sequence positions.

## Step 6: Analyze Interactions

1. Query STRING for protein-protein interactions:
   - Use `life-sciences-proteomics` → `string_query` tool.
2. Identify interaction partners and confidence scores.
3. Cross-reference with structural data for interface analysis.

## Expected Outputs
- Structure summary with PDB ID, resolution, and method.
- AlphaFold confidence assessment for predicted regions.
- Domain classification from CATH.
- Functional annotations from UniProt.
