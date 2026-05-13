---
inclusion: auto
fileMatchPattern: "**/*metabol*,**/*hmdb*,**/*massbank*"
---

# Metabolite Identification

Step-by-step guide using HMDB, MetaboLights, and MassBank for metabolite identification.

## Step 1: Search HMDB by Name or Mass

1. Search HMDB for a metabolite:
   - Use `life-sciences-metabolomics` → `hmdb_search` tool with metabolite name or exact mass.
2. Review results: HMDB ID, name, chemical formula, molecular weight.
3. Get detailed metabolite information including pathways and biofluid locations.

## Step 2: Query MetaboLights for Experimental Data

1. Search MetaboLights for studies involving the metabolite:
   - Use `life-sciences-metabolomics` → `metabolights_search` tool.
2. Review study metadata: organism, analytical platform, study design.
3. Access raw and processed data for reference spectra.

## Step 3: Match MS/MS Spectra with MassBank

1. Search MassBank with precursor m/z and MS/MS spectrum:
   - Use `life-sciences-metabolomics` → `massbank_search` tool.
2. Set matching parameters: mass tolerance (± 0.01 Da), minimum score (0.7).
3. Review matched spectra with cosine similarity scores.
4. Compare fragmentation patterns for confident identification.

## Step 4: Cross-Reference Results

1. Compare identifications across HMDB, MetaboLights, and MassBank.
2. Assign MSI confidence level:
   - Level 1: Matches authentic standard (RT + MS/MS).
   - Level 2: Spectral library match (MS/MS only).
   - Level 3: Compound class match.
3. Note any discrepancies for manual review.

## Step 5: Pathway Context

1. Look up metabolite pathways in HMDB or KEGG.
2. Identify related metabolites in the same pathway.
3. Check if pathway enrichment supports the identification.

## Expected Outputs
- Metabolite identification with MSI confidence level.
- Spectral match scores from MassBank.
- Pathway context from HMDB/KEGG.
- Cross-reference IDs (HMDB, ChEBI, KEGG, PubChem).
