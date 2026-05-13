---
inclusion: manual
---

# Metabolomics Analysis

Practical guidance for metabolite identification, spectral matching, pathway enrichment, and statistical analysis.

## Metabolite Identification

### Identification Confidence Levels (MSI)
- **Level 1**: Confirmed by comparison with authentic standard (same retention time + MS/MS).
- **Level 2**: Putatively annotated by spectral library match (MS/MS match only).
- **Level 3**: Putatively characterized compound class (partial match).
- **Level 4**: Unknown — unidentified but reproducible signal.

### Identification Workflow
1. Acquire MS/MS spectra for features of interest.
2. Search spectral libraries (HMDB, MassBank, METLIN, mzCloud).
3. Match by precursor m/z (± 5 ppm), fragmentation pattern, and retention time.
4. Confirm Level 1 hits with authentic standards when available.
5. Use in silico fragmentation (CFM-ID, MetFrag) for Level 2 annotation.

### Mass Accuracy
- **High-resolution MS** (Orbitrap, Q-TOF): < 5 ppm mass accuracy.
- Calculate molecular formula candidates from exact mass.
- Use isotope pattern and ring-double bond equivalence (RDBE) for filtering.

## Spectral Matching

### Scoring Methods
- **Cosine similarity**: Standard dot-product score between query and reference spectra.
- **Modified cosine**: Accounts for precursor mass shift (useful for analogs).
- **Entropy similarity**: Information-theoretic approach, robust to noise.

### Best Practices
- Set minimum cosine score threshold: 0.7 for confident matches.
- Require minimum 4 matched fragment peaks.
- Filter by precursor mass tolerance (± 0.01 Da for high-res data).
- Use molecular networking (GNPS) to propagate annotations to related spectra.

```python
# Example: cosine similarity between two spectra
import numpy as np

def cosine_similarity(spec1, spec2, tolerance=0.01):
    """Calculate cosine similarity between two mass spectra."""
    matched_intensity_1, matched_intensity_2 = [], []
    for mz1, int1 in spec1:
        for mz2, int2 in spec2:
            if abs(mz1 - mz2) <= tolerance:
                matched_intensity_1.append(int1)
                matched_intensity_2.append(int2)
                break
    if not matched_intensity_1:
        return 0.0
    v1, v2 = np.array(matched_intensity_1), np.array(matched_intensity_2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
```

## Pathway Enrichment

### Over-Representation Analysis (ORA)
- Input: list of significant metabolites (e.g., p < 0.05, fold change > 2).
- Test: hypergeometric test or Fisher's exact test against pathway databases.
- Databases: KEGG, Reactome, SMPDB (Small Molecule Pathway Database).
- Correct for multiple testing (Benjamini-Hochberg FDR).

### Quantitative Enrichment Analysis (QEA)
- Input: concentration table for all measured metabolites.
- Test: Global test or GSEA-style enrichment using metabolite-level statistics.
- More powerful than ORA when quantitative data is available.

### Pathway Databases
| Database | Coverage | Access |
|----------|----------|--------|
| KEGG | Comprehensive metabolic pathways | KEGG API |
| Reactome | Curated human pathways | Reactome API |
| SMPDB | Small molecule pathways | MetaboAnalyst |
| WikiPathways | Community-curated pathways | WikiPathways API |

## Statistical Analysis

### Univariate Methods
- **t-test / Wilcoxon**: Two-group comparison. Use Welch's t-test for unequal variances.
- **ANOVA / Kruskal-Wallis**: Multi-group comparison.
- **Volcano plot**: Visualize fold change vs. significance.

### Multivariate Methods
- **PCA**: Unsupervised overview of sample clustering and outlier detection.
- **PLS-DA**: Supervised classification and feature selection.
- **OPLS-DA**: Orthogonal PLS-DA for cleaner separation of group differences.
- Validate with permutation testing (n=1000) and cross-validation (Q² > 0.5).

## Normalization Methods

### Sample Normalization
- **Total ion current (TIC)**: Divide by sum of all peak intensities.
- **Probabilistic quotient normalization (PQN)**: Robust to large fold changes.
- **Internal standard**: Normalize to spiked-in reference compounds.

### Data Transformation
- **Log transformation**: Reduce skewness, stabilize variance.
- **Pareto scaling**: Divide by square root of standard deviation. Good balance.
- **Auto-scaling**: Mean-center and divide by standard deviation. Equal weight to all features.

### Quality Control
- Include pooled QC samples every 5–10 injections.
- Filter features by CV in QC samples (keep CV < 30%).
- Correct batch effects with QC-based LOESS regression.

## Tools and Resources
- **HMDB**: Human Metabolome Database — metabolite reference data.
- **MetaboLights**: Public metabolomics data repository.
- **MassBank**: Mass spectral reference library.
- **MetaboAnalyst**: Web-based metabolomics data analysis platform.
- Use the metabolomics MCP server for programmatic access to HMDB, MetaboLights, METLIN, and MassBank.
