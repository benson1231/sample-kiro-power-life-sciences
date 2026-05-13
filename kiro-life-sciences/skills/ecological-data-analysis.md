---
inclusion: manual
---

# Ecological Data Analysis

Practical guidance for species distribution modeling, biodiversity metrics, eDNA analysis, and occurrence data handling.

## Species Distribution Modeling (SDM)

### Workflow Overview
1. Obtain occurrence records from GBIF, iNaturalist, or field surveys.
2. Clean and filter records (remove duplicates, spatial outliers, coordinate errors).
3. Obtain environmental layers (WorldClim, CHELSA, MODIS).
4. Fit models using MaxEnt, random forest, or ensemble approaches.
5. Project distributions under current and future climate scenarios.

### Data Preparation
- Thin occurrence points to reduce spatial autocorrelation (minimum 1 km apart).
- Generate pseudo-absences or background points within the study extent.
- Check for sampling bias and apply bias correction if needed.

```python
# Example: spatial thinning with spThin
from sklearn.neighbors import BallTree
import numpy as np

def thin_occurrences(coords, min_distance_km=1.0):
    tree = BallTree(np.radians(coords), metric='haversine')
    keep = np.ones(len(coords), dtype=bool)
    for i in range(len(coords)):
        if keep[i]:
            neighbors = tree.query_radius([np.radians(coords[i])],
                                          r=min_distance_km / 6371.0)[0]
            for j in neighbors:
                if j != i:
                    keep[j] = False
    return coords[keep]
```

### Model Evaluation
- Use AUC (Area Under the ROC Curve) — aim for > 0.7.
- Use TSS (True Skill Statistic) — aim for > 0.4.
- Perform k-fold spatial cross-validation to avoid spatial autocorrelation bias.

## Biodiversity Metrics

### Alpha Diversity
- **Shannon Index (H')**: Accounts for richness and evenness. Range: 0 to ~5.
  - `H' = -Σ(pi × ln(pi))` where pi is the proportion of species i.
- **Simpson Index (D)**: Probability that two individuals belong to different species.
  - `D = 1 - Σ(pi²)`
- **Species Richness (S)**: Simple count of species in a sample.

### Beta Diversity
- **Jaccard Index**: Proportion of shared species between two sites.
- **Bray-Curtis Dissimilarity**: Quantitative measure of community composition difference.
- **Sørensen Index**: Similar to Jaccard but gives more weight to shared species.

### Gamma Diversity
- Total species diversity across all sites in a landscape.
- `γ = α × β` (multiplicative partitioning).

## Environmental DNA (eDNA) Analysis

### Workflow
1. Collect water/soil samples with contamination controls.
2. Extract DNA using commercial kits (e.g., DNeasy PowerWater).
3. Amplify target markers (COI for animals, ITS for fungi, 16S for bacteria).
4. Sequence with Illumina MiSeq or Oxford Nanopore.
5. Process with bioinformatics pipeline (DADA2, OBITools, or QIIME 2).
6. Assign taxonomy against reference databases (BOLD, SILVA, UNITE).

### Quality Control
- Include field blanks, extraction blanks, and PCR negatives.
- Remove sequences below minimum read count threshold (typically 10 reads).
- Filter by sequence length and quality score.

## Occurrence Data Handling

### Data Sources
- **GBIF**: Global biodiversity occurrence records (use ecology MCP server).
- **iNaturalist**: Community science observations with photo verification.
- **BOLD**: Barcode of Life Data System for DNA barcode records.
- **IUCN Red List**: Conservation status and range maps.

### Data Cleaning Checklist
- Remove records with zero or null coordinates.
- Flag records in the ocean for terrestrial species (and vice versa).
- Remove records with coordinate precision > 10 km for fine-scale analyses.
- Check for country-coordinate mismatches.
- Remove fossil and preserved specimen records if modeling current distributions.
- Standardize taxonomy using NCBI Taxonomy or GBIF backbone.

### Darwin Core Standard
- Use Darwin Core terms for occurrence data exchange.
- Key fields: `scientificName`, `decimalLatitude`, `decimalLongitude`, `eventDate`, `basisOfRecord`.
- Use `occurrenceStatus` to distinguish presence from absence records.
