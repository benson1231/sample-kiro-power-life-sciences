---
inclusion: auto
fileMatchPattern: "**/*single*cell*,**/*scrnaseq*,**/*10x*,**/*cellxgene*"
---

# Single-Cell RNA-seq Analysis

Step-by-step guide using CellxGene datasets and Single Cell Expression Atlas for scRNA-seq analysis.

## Step 1: Browse CellxGene Datasets

1. Search for datasets by tissue, disease, or organism:
   - Use `life-sciences-cellbiology` → `cellxgene_datasets` tool.
2. Review dataset metadata: cell count, tissue, disease, organism, assay.
3. Select a dataset for analysis or comparison.

## Step 2: Query Gene Expression

1. Query expression of genes of interest:
   - Use `life-sciences-cellbiology` → `cellxgene_expression` tool with gene names.
2. View expression across cell types and conditions.
3. Identify cell types with high expression of your target genes.

## Step 3: Cross-Reference with Single Cell Expression Atlas

1. Search SCEA for additional datasets:
   - Use `life-sciences-cellbiology` → `scea_search` tool.
2. Compare expression patterns across independent datasets.
3. Validate cell type-specific expression findings.

## Step 4: Cell Type Annotation

1. Use reference datasets for automated cell type annotation.
2. Compare cluster marker genes with known cell type signatures.
3. Validate annotations with multiple reference sources.

## Step 5: Differential Expression Analysis

1. Identify differentially expressed genes between conditions or cell types.
2. Use Wilcoxon rank-sum test for quick analysis.
3. Use pseudobulk methods (DESeq2) for multi-sample designs.
4. Filter by log fold change (> 0.25) and adjusted p-value (< 0.05).

## Step 6: Pathway and Gene Set Analysis

1. Perform gene set enrichment on DE genes.
2. Query pathway databases (KEGG, Reactome) for enriched pathways.
3. Identify biological processes driving differences between cell states.

## Expected Outputs
- Gene expression profiles across cell types.
- Cell type annotations validated across datasets.
- Differentially expressed gene lists with statistics.
- Enriched pathways and biological processes.
