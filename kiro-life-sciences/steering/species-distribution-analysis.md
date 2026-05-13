---
inclusion: auto
fileMatchPattern: "**/*species*,**/*occurrence*,**/*biodiversity*,**/*gbif*"
---

# Species Distribution Analysis

Step-by-step guide using GBIF, IUCN Red List, and iNaturalist for species distribution modeling.

## Step 1: Search GBIF for Occurrences

1. Search for species occurrences:
   - Use `life-sciences-ecology` → `gbif_occurrences` tool with species name.
2. Filter by geographic bounds, date range, and basis of record.
3. Download occurrence records with coordinates.

## Step 2: Check Conservation Status

1. Query IUCN Red List for the species:
   - Use `life-sciences-ecology` → `iucn_species` tool (requires API key).
2. Review conservation status: LC, NT, VU, EN, CR, EW, EX.
3. Note population trend and habitat information.

## Step 3: Supplement with iNaturalist Observations

1. Search iNaturalist for recent observations:
   - Use `life-sciences-ecology` → `inaturalist_search` tool.
2. Filter for research-grade observations only.
3. Merge with GBIF data, removing duplicates by coordinate proximity.

## Step 4: Clean Occurrence Data

1. Remove records with missing or zero coordinates.
2. Remove spatial outliers (records far from known range).
3. Thin records to reduce spatial autocorrelation (1 km minimum distance).
4. Standardize taxonomy using NCBI Taxonomy or GBIF backbone.

## Step 5: Build Distribution Model

1. Obtain environmental layers (WorldClim bioclimatic variables).
2. Generate background/pseudo-absence points within study extent.
3. Fit species distribution model (MaxEnt, random forest, or ensemble).
4. Evaluate model performance (AUC > 0.7, TSS > 0.4).

## Step 6: Project and Visualize

1. Project distribution under current climate.
2. Optionally project under future climate scenarios (SSP2-4.5, SSP5-8.5).
3. Map predicted suitable habitat and range shifts.

## Expected Outputs
- Cleaned occurrence dataset with coordinates and metadata.
- Conservation status and population trend from IUCN.
- Species distribution model with performance metrics.
- Habitat suitability maps under current and future scenarios.
