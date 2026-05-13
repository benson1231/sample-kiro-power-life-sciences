---
inclusion: auto
fileMatchPattern: "**/*image*,**/*microscop*,**/*dicom*,**/*.tif"
---

# Biomedical Image Analysis

Step-by-step guide using OMERO, CellProfiler, and ImageJ for biomedical image analysis.

## Step 1: Import Images to OMERO

1. Upload images to OMERO server:
   - Use `life-sciences-imaging` → `omero_import` tool with image file path.
2. Organize images into projects and datasets.
3. Add metadata annotations (experiment, channel names, pixel size).

## Step 2: Preprocess Images

1. Apply background subtraction:
   - Use `life-sciences-imaging` → `imagej_macro` tool with rolling ball algorithm.
2. Correct illumination unevenness if needed.
3. Enhance contrast with CLAHE or histogram equalization.

## Step 3: Segment with CellProfiler

1. Set up a CellProfiler pipeline:
   - Use `life-sciences-imaging` → `cellprofiler_pipeline` tool.
2. Identify primary objects (nuclei) using Otsu thresholding.
3. Identify secondary objects (cells) by propagation from nuclei.
4. Identify tertiary objects (cytoplasm) by subtracting nuclei from cells.

## Step 4: Extract Features

1. Measure object properties:
   - Morphology: area, perimeter, eccentricity, form factor.
   - Intensity: mean, integrated, standard deviation per channel.
   - Texture: Haralick features from GLCM.
2. Export measurements to CSV for downstream analysis.

## Step 5: Analyze with ImageJ

1. For custom analysis, run ImageJ macros:
   - Use `life-sciences-imaging` → `imagej_macro` tool.
2. Perform particle analysis, colocalization, or intensity profiling.
3. Generate overlay images with segmentation outlines.

## Step 6: Quantify and Report

1. Aggregate measurements across images and conditions.
2. Perform statistical comparisons between treatment groups.
3. Generate summary plots (box plots, scatter plots, heatmaps).

## Expected Outputs
- Segmented images with object outlines.
- Feature measurements per cell/object in CSV format.
- Statistical comparison between experimental conditions.
- Representative images with annotations.
