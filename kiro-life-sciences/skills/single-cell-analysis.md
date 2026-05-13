---
inclusion: manual
---

# Single-Cell Analysis

Practical guidance for scRNA-seq QC, normalization, clustering, differential expression, and trajectory inference.

## QC Metrics

### Per-Cell QC
- **Total UMI counts**: Remove cells with very low counts (empty droplets) or very high counts (doublets).
- **Number of detected genes**: Minimum 200–500 genes per cell (dataset-dependent).
- **Mitochondrial gene percentage**: High % (> 20–25%) indicates dying or stressed cells.
- **Ribosomal gene percentage**: Informational; not typically used for filtering.

### Per-Gene QC
- Remove genes detected in fewer than 3 cells.
- Remove mitochondrial and ribosomal genes if not relevant to analysis.

### Doublet Detection
- Use Scrublet, DoubletFinder, or scDblFinder.
- Expected doublet rate: ~0.8% per 1000 cells captured.
- Remove predicted doublets before downstream analysis.

```python
import scanpy as sc

adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

# Filter cells
sc.pp.filter_cells(adata, min_genes=200)
adata = adata[adata.obs.pct_counts_mt < 20, :]
sc.pp.filter_genes(adata, min_cells=3)
```

## Normalization

### scran (Pool-Based)
- Deconvolution-based size factor estimation.
- Handles zero-inflated data well.
- Recommended for datasets with diverse cell types.

### SCTransform (Variance Stabilization)
- Regularized negative binomial regression.
- Simultaneously normalizes and selects variable features.
- Default in Seurat v4+ workflows.

### Simple Normalization
- **Library size normalization**: Scale each cell to a target sum (e.g., 10,000).
- **Log transformation**: `log1p(x)` after library size normalization.
- Quick and effective for many analyses.

```python
# Scanpy standard normalization
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
```

## Dimensionality Reduction

### PCA
- Run on highly variable genes (top 2000–3000).
- Use elbow plot to select number of PCs (typically 15–50).

### UMAP / t-SNE
- UMAP preferred for most visualizations (preserves global structure better).
- Use PCA coordinates as input (not raw expression).
- UMAP parameters: `n_neighbors=15`, `min_dist=0.5` (adjust for dataset).

## Clustering

### Leiden Algorithm (Recommended)
- Community detection on k-nearest neighbor graph.
- Resolution parameter controls granularity (0.1 = few clusters, 2.0 = many).
- More robust than Louvain; guaranteed to find well-connected communities.

### Louvain Algorithm
- Classic community detection method.
- Faster than Leiden but may produce poorly connected communities.
- Use Leiden unless computational resources are limited.

### Choosing Resolution
- Start with resolution 0.5–1.0 and adjust based on biological expectations.
- Use clustree (R) or multiple resolutions to assess stability.
- Validate clusters with known marker genes.

```python
sc.pp.neighbors(adata, n_pcs=30)
sc.tl.leiden(adata, resolution=0.8)
sc.tl.umap(adata)
sc.pl.umap(adata, color='leiden')
```

## Differential Expression

### Methods
- **Wilcoxon rank-sum test**: Non-parametric, robust, fast. Default in Scanpy.
- **MAST**: Hurdle model accounting for dropout. Good for small datasets.
- **Pseudobulk**: Aggregate cells per sample, then use DESeq2/edgeR. Best for multi-sample designs.

### Best Practices
- Compare one cluster vs. rest, or specific cluster pairs.
- Filter by log fold change (> 0.25) and adjusted p-value (< 0.05).
- Use pseudobulk methods when you have biological replicates.

```python
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=20)
```

## Cell Type Annotation

### Manual Annotation
- Use known marker genes to assign cell types to clusters.
- Cross-reference with published single-cell atlases.

### Automated Annotation
- **CellTypist**: Pre-trained models for immune and other cell types.
- **scType**: Marker-based annotation using curated gene sets.
- **SingleR**: Reference-based annotation using bulk RNA-seq profiles.

## Trajectory Inference

### Monocle 3
- Learns principal graph through UMAP space.
- Identifies pseudotime ordering and branch points.
- Best for: developmental trajectories, differentiation paths.

### PAGA (Partition-based Graph Abstraction)
- Builds coarse-grained graph of cluster connectivity.
- Identifies likely transition paths between cell states.
- Best for: complex topologies, multiple lineages.

### RNA Velocity (scVelo)
- Uses spliced/unspliced RNA ratios to infer future cell states.
- Provides directional information on differentiation.
- Requires data from 10x Chromium with intronic reads.

## Tools and Resources
- **CellxGene**: Interactive explorer for single-cell datasets.
- **Single Cell Expression Atlas**: Curated scRNA-seq datasets from EMBL-EBI.
- **Cell Atlas**: Reference maps of cell types across tissues.
- Use the cell biology MCP server for programmatic access to CellxGene and SCEA.
