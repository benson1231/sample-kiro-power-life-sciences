---
inclusion: auto
fileMatchPattern: "**/*epigenom*,**/*methylat*,**/*chromatin*,**/*histone*"
---

# Epigenomics Analysis

Step-by-step guide using IHEC, Roadmap Epigenomics, and ENCODE for epigenomic data analysis.

## Step 1: Search IHEC Data Portal

1. Search for epigenomic datasets:
   - Use `life-sciences-epigenomics` → `ihec_search` tool with tissue or cell type.
2. Filter by assay type: ChIP-seq, WGBS, ATAC-seq, RNA-seq.
3. Review available datasets and their metadata.

## Step 2: Query Roadmap Epigenomics

1. Search Roadmap for chromatin state maps:
   - Use `life-sciences-epigenomics` → `roadmap_search` tool.
2. Retrieve chromatin state annotations (15-state or 18-state ChromHMM model).
3. Identify active promoters, enhancers, and repressed regions for your tissue of interest.

## Step 3: Integrate with ENCODE Data

1. Search ENCODE for complementary functional genomics data:
   - Use `life-sciences-genomics` → `encode_search` tool.
2. Find ChIP-seq experiments for transcription factors and histone marks.
3. Download peak files and signal tracks for integration.

## Step 4: Analyze Chromatin States

1. Map your regions of interest to chromatin states.
2. Identify regulatory elements (enhancers, promoters) overlapping your regions.
3. Compare chromatin states across tissues or conditions.

## Step 5: Methylation Analysis

1. For WGBS data, query methylation levels at CpG sites.
2. Identify differentially methylated regions (DMRs) between conditions.
3. Correlate methylation changes with gene expression changes.

## Step 6: Integrate Multi-Omics

1. Overlay epigenomic data with gene expression (RNA-seq).
2. Identify genes with concordant epigenetic and expression changes.
3. Map regulatory variants to active enhancers and promoters.

## Expected Outputs
- Chromatin state maps for tissues of interest.
- Regulatory element annotations (enhancers, promoters).
- Differentially methylated regions with associated genes.
- Integrated epigenomic-transcriptomic analysis.
