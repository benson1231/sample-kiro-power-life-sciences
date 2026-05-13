---
inclusion: auto
fileMatchPattern: "**/*clinvar*,**/*variant*,**/*disease*"
---

# Gene-Disease Association Analysis

Step-by-step guide to cross-reference gene-disease associations across ClinVar, OMIM, HPO, and Disease Ontology.

## Step 1: Query ClinVar for Variant-Disease Links

1. Search ClinVar by gene name (e.g., "BRCA1"):
   - Use `life-sciences-genomics` → `clinvar_search` tool.
2. Review returned variants with clinical significance (Pathogenic, Likely Pathogenic).
3. Note associated conditions and ClinVar variation IDs.

## Step 2: Cross-Reference with OMIM

1. For each associated condition, query OMIM:
   - Use `life-sciences-clinical` → `omim_search` tool with the disease name.
2. Retrieve OMIM entry details including inheritance pattern and molecular basis.
3. Note OMIM phenotype MIM numbers for further cross-referencing.

## Step 3: Map to HPO Terms

1. Query HPO for phenotypic features associated with the disease:
   - Use `life-sciences-ontologies` → `hpo_search` tool with the disease name or OMIM ID.
2. Retrieve the list of HPO terms (phenotypic abnormalities).
3. Identify the most specific phenotype terms for clinical matching.

## Step 4: Query Disease Ontology

1. Search Disease Ontology for the disease:
   - Use `life-sciences-ontologies` → `disease_ontology_search` tool.
2. Retrieve the DO term with cross-references to OMIM, MeSH, ICD-10.
3. Use the DO hierarchy to find related diseases and parent terms.

## Step 5: Compile Cross-Referenced Results

1. Create a summary table linking:
   - Gene → ClinVar variants → OMIM entries → HPO phenotypes → DO terms.
2. Identify variants with consistent pathogenic evidence across databases.
3. Note any discrepancies between databases for further investigation.

## Expected Outputs
- Gene-disease association table with evidence from multiple databases.
- List of HPO phenotype terms for clinical phenotype matching.
- Cross-reference IDs (ClinVar, OMIM, HPO, DO) for each association.
