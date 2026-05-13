---
inclusion: auto
fileMatchPattern: "**/*resistance*,**/*amr*,**/*antibiotic*,**/*antimicrobial*"
---

# Antimicrobial Resistance Analysis

Step-by-step guide using CARD and BV-BRC for antimicrobial resistance profiling.

## Step 1: Search CARD for Resistance Genes

1. Search the Comprehensive Antibiotic Resistance Database:
   - Use `life-sciences-microbiology` → `card_search` tool with gene name or antibiotic.
2. Review results: ARO (Antibiotic Resistance Ontology) terms, resistance mechanism, gene family.
3. Get detailed information on resistance determinants.

## Step 2: Identify Resistance Mechanisms

1. For each resistance gene, review the mechanism:
   - Antibiotic inactivation (e.g., beta-lactamases).
   - Target modification (e.g., ribosomal methylation).
   - Efflux pumps (e.g., MexAB-OprM).
   - Target replacement (e.g., mecA for MRSA).
2. Note the antibiotics affected by each mechanism.

## Step 3: Genome-Level Analysis with BV-BRC

1. Submit genome sequence to BV-BRC for analysis:
   - Use `life-sciences-microbiology` → `bvbrc_genome_search` tool.
2. Retrieve genome annotations including AMR gene predictions.
3. Review specialty gene annotations for virulence and resistance.

## Step 4: Resistance Profiling

1. Compile all identified resistance genes and mechanisms.
2. Map resistance genes to antibiotic classes:
   - Beta-lactams, aminoglycosides, fluoroquinolones, tetracyclines, etc.
3. Predict phenotypic resistance based on genotypic findings.

## Step 5: Epidemiological Context

1. Check if resistance genes are on mobile genetic elements (plasmids, transposons).
2. Assess horizontal gene transfer risk.
3. Compare resistance profiles with regional surveillance data.

## Step 6: Report and Recommend

1. Generate resistance profile summary.
2. List effective antibiotics (no resistance detected).
3. Flag antibiotics with predicted resistance.
4. Note any novel or unusual resistance mechanisms.

## Expected Outputs
- Complete AMR gene inventory with mechanisms.
- Antibiotic susceptibility prediction.
- Resistance gene location (chromosomal vs. mobile element).
- Treatment recommendations based on resistance profile.
