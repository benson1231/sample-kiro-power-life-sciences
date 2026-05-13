---
inclusion: auto
fileMatchPattern: "**/*microbiome*,**/*16s*,**/*metagenom*"
---

# Microbiome Analysis

Step-by-step guide using SILVA, QIIME 2, and MG-RAST for microbiome profiling.

## Step 1: Assign Taxonomy with SILVA

1. Search SILVA for reference sequences:
   - Use `life-sciences-microbiology` → `silva_search` tool with 16S/18S query.
2. Download the appropriate SILVA reference database (SSU or LSU).
3. Use SILVA taxonomy for classification of amplicon sequences.

## Step 2: Run QIIME 2 Pipeline

1. Import raw sequencing data into QIIME 2 format:
   - Use `life-sciences-microbiology` → `qiime2_import` tool.
2. Denoise with DADA2 or Deblur to generate ASVs (Amplicon Sequence Variants).
3. Assign taxonomy using the SILVA classifier.
4. Generate diversity metrics (alpha: Shannon, Simpson; beta: Bray-Curtis, UniFrac).

## Step 3: Annotate with MG-RAST

1. For shotgun metagenomics data, submit to MG-RAST:
   - Use `life-sciences-microbiology` → `mgrast_submit` tool.
2. Monitor job status until analysis completes.
3. Retrieve functional annotations (SEED, COG, KEGG) and taxonomic profiles.

## Step 4: Analyze Results

1. Compare alpha diversity between sample groups.
2. Perform beta diversity analysis with PCoA ordination.
3. Identify differentially abundant taxa (LEfSe, ANCOM, or ALDEx2).
4. Correlate microbial composition with environmental or clinical metadata.

## Step 5: Antimicrobial Resistance Profiling

1. Screen for resistance genes using CARD:
   - Use `life-sciences-microbiology` → `card_search` tool.
2. Identify resistance mechanisms and associated antibiotics.
3. Cross-reference with BV-BRC for genome-level resistance analysis.

## Expected Outputs
- ASV/OTU table with taxonomy assignments.
- Alpha and beta diversity metrics.
- Functional annotation profiles from MG-RAST.
- Differentially abundant taxa between groups.
