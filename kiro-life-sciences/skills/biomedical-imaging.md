---
inclusion: manual
---

# Biomedical Imaging

Practical guidance for image preprocessing, segmentation, feature extraction, DICOM handling, and microscopy analysis.

## Image Preprocessing

### Common Steps
1. **Noise reduction**: Gaussian blur, median filter, or non-local means denoising.
2. **Contrast enhancement**: Histogram equalization, CLAHE (Contrast Limited Adaptive Histogram Equalization).
3. **Background subtraction**: Rolling ball algorithm or flat-field correction.
4. **Registration**: Align multi-channel or time-series images to a common reference.

### Microscopy-Specific
- **Illumination correction**: Correct uneven illumination with flat-field images.
- **Deconvolution**: Restore resolution lost to optical diffraction (Richardson-Lucy, Wiener).
- **Z-stack projection**: Maximum intensity projection (MIP) or extended depth of focus.

```python
# Example: CLAHE with scikit-image
from skimage import exposure
enhanced = exposure.equalize_adapthist(image, clip_limit=0.03)
```

## Segmentation Algorithms

### Thresholding
- **Otsu's method**: Automatic threshold selection for bimodal histograms.
- **Adaptive thresholding**: Local threshold for uneven illumination.
- Best for: high-contrast images with clear foreground/background separation.

### Watershed
- Marker-based segmentation for touching or overlapping objects.
- Requires seed points (from local maxima of distance transform).
- Best for: cell segmentation in dense cultures.

### Deep Learning
- **U-Net**: Encoder-decoder architecture for biomedical image segmentation.
- **Cellpose**: Pre-trained model for cell and nucleus segmentation.
- **StarDist**: Star-convex polygon detection for nucleus segmentation.
- Best for: complex morphologies, variable staining, large datasets.

### Region Growing
- Start from seed points and expand based on similarity criteria.
- Best for: segmenting connected regions with homogeneous intensity.

## Feature Extraction

### Morphological Features
- Area, perimeter, circularity, eccentricity, solidity.
- Useful for cell phenotyping and morphological profiling.

### Intensity Features
- Mean, median, standard deviation, min, max intensity per object.
- Integrated intensity (total fluorescence) for quantification.

### Texture Features
- Haralick features from gray-level co-occurrence matrix (GLCM).
- Local binary patterns (LBP) for texture classification.
- Gabor filters for orientation-sensitive texture analysis.

```python
# Example: extract features with scikit-image
from skimage.measure import regionprops
props = regionprops(label_image, intensity_image=raw_image)
for cell in props:
    print(f"Area: {cell.area}, Mean intensity: {cell.mean_intensity}")
```

## DICOM Handling

### Reading DICOM Files
```python
import pydicom
ds = pydicom.dcmread('scan.dcm')
pixel_data = ds.pixel_array
patient_id = ds.PatientID
modality = ds.Modality  # CT, MR, US, etc.
```

### Key DICOM Tags
| Tag | Description | Example |
|-----|-------------|---------|
| (0010,0020) | Patient ID | "PAT001" |
| (0008,0060) | Modality | "CT", "MR" |
| (0028,0010) | Rows | 512 |
| (0028,0011) | Columns | 512 |
| (0028,0030) | Pixel Spacing | [0.5, 0.5] |
| (0020,0032) | Image Position | [-250, -250, -100] |

### De-identification
- Remove or replace PHI tags before sharing (PatientName, PatientID, dates).
- Use pydicom's `anonymize` or CTP (Clinical Trial Processor).
- Retain imaging-relevant tags (PixelSpacing, SliceThickness, Modality).

## Microscopy Image Analysis Pipelines

### CellProfiler Pipeline
1. Load images (multi-channel TIFF or OME-TIFF).
2. Identify nuclei (primary objects) using Otsu or Cellpose.
3. Identify cells (secondary objects) by expanding from nuclei.
4. Measure morphology, intensity, and texture per cell.
5. Export measurements to CSV for downstream analysis.

### ImageJ/Fiji Macro
```javascript
// Basic cell counting macro
run("Subtract Background...", "rolling=50");
run("Auto Threshold", "method=Otsu");
run("Watershed");
run("Analyze Particles...", "size=50-Infinity circularity=0.3-1.0 show=Outlines");
```

### High-Content Screening
- Use plate-based layouts with well identifiers.
- Normalize features per plate (z-score or percent of control).
- Apply multivariate analysis (PCA, t-SNE, UMAP) for phenotype clustering.

## Tools and Resources
- **OMERO**: Image data management platform for microscopy.
- **CellProfiler**: Open-source image analysis for high-throughput screens.
- **ImageJ/Fiji**: General-purpose image analysis with extensive plugin ecosystem.
- **napari**: Python-based viewer for multi-dimensional image data.
- **BioImage Archive**: Public repository for biological image datasets.
- Use the imaging MCP server for programmatic access to OMERO, CellProfiler, and ImageJ.
