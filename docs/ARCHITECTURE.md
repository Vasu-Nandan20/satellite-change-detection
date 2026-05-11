# SENTINEL — Architecture Documentation

## System Architecture

This document describes the technical architecture of the SENTINEL Satellite Change Detection System.

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        SENTINEL v2.0                             │
│                  Satellite Change Detection                      │
├──────────────┬──────────────────┬───────────────────────────────┤
│   GUI Layer  │   Engine Layer   │        Utility Layer           │
│  (gui/)      │   (engine/)      │        (utils/)                │
├──────────────┼──────────────────┼───────────────────────────────┤
│ AppWindow    │ ImageAligner     │ ImageUtils                     │
│ Dashboard    │ ChangeDetector   │ ReportGenerator                │
│ Detection    │ ChangeClassifier │                                │
│ Analytics    │ ChangeAnalyzer   │                                │
│ History      │                  │                                │
│ Settings     │                  │                                │
├──────────────┴──────────────────┴───────────────────────────────┤
│                    External Libraries                            │
│  OpenCV │ scikit-image │ scikit-learn │ matplotlib │ ReportLab   │
└─────────────────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. Model-View-Controller (MVC)
- **Model (Engine)**: `alignment.py`, `detector.py`, `classifier.py`, `analyzer.py`
- **View (GUI)**: CustomTkinter frames in `gui/` package
- **Controller**: `detection_frame.py` orchestrates the pipeline

### 2. Strategy Pattern
- `ImageAligner` supports multiple alignment strategies (ORB, SIFT, ECC)
- `ChangeDetector` supports multiple detection strategies (AbsDiff, SSIM, Combined)
- Strategy is selected at runtime via dropdown menus

### 3. Observer Pattern
- Detection frame notifies Analytics frame when new results are available
- Dashboard reads from CSV log to display latest stats

## Detection Pipeline

```
Input Images (Before + After)
        │
        ▼
┌───────────────┐
│  Resize &     │  Match dimensions of both images
│  Normalize    │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Image        │  Register target to reference
│  Alignment    │  Methods: ORB (fast), SIFT (accurate), ECC (sub-pixel)
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Change       │  Detect pixel-level differences
│  Detection    │  Methods: AbsDiff, SSIM, Combined
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Morphological│  Remove noise: Open (remove small), Close (fill holes)
│  Cleaning     │  Elliptical kernels: 3×3 and 7×7
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Contour      │  Extract external contours from binary mask
│  Extraction   │  Filter by minimum area threshold
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Change       │  Classify each contour by type:
│  Classification│  HSV color analysis + brightness + geometry
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Analytics    │  Compute summary stats, heatmap, density grid
│  & Reporting  │  Generate PDF/CSV reports
└───────────────┘
```

## Classification Algorithm

The classifier uses a rule-based approach with the following decision tree:

```
For each detected contour:
  1. Extract ROI from before and after images
  2. Convert to HSV color space
  3. Compute mean Hue, Saturation, Value

  IF green_hue_shift (H: 35-85, S > 40):
      → "Vegetation Change"
  ELIF blue_hue_shift (H: 90-130, S > 30):
      → "Water Change"
  ELIF brightness_increase > 20:
      → "Construction"
  ELIF brightness_decrease > 20:
      → "Demolition"
  ELIF large_area AND regular_shape:
      → "Construction"
  ELSE:
      → "Other"
```

## Threading Model

```
┌──────────────┐         ┌──────────────┐
│  Main Thread │         │ Worker Thread │
│  (GUI/Tk)    │         │ (Detection)   │
├──────────────┤         ├──────────────┤
│ Handle UI    │ start() │ Run pipeline  │
│ events       │────────►│ Update prog.  │
│              │         │ via after()   │
│ Display      │◄────────│ Store results │
│ results      │ after() │               │
└──────────────┘         └──────────────┘
```

- Detection runs on a daemon thread to prevent UI freezing
- Progress updates use `widget.after()` for thread-safe GUI updates
- Results are stored in shared state and rendered on main thread

## Data Flow

```
User Input          Processing              Output
──────────          ──────────              ──────
before.jpg    ──►  alignment.py      ──►  annotated image
after.jpg     ──►  detector.py       ──►  heatmap overlay
settings      ──►  classifier.py     ──►  change mask
                   analyzer.py       ──►  PDF report
                                     ──►  CSV export
                                     ──►  change_log.csv
                                     ──►  matplotlib charts
```

## Dependencies

| Package | Version | Purpose | Layer |
|---------|---------|---------|-------|
| opencv-contrib-python | 4.13+ | Image processing, SIFT/ORB | Engine |
| scikit-image | 0.26+ | SSIM computation | Engine |
| scikit-learn | 1.8+ | KMeans clustering | Engine |
| numpy | 2.0+ | Array operations | Engine |
| customtkinter | 5.2+ | Modern GUI framework | GUI |
| matplotlib | 3.10+ | Embedded charts | GUI |
| pillow | 11.0+ | Image format conversion | Utility |
| reportlab | 4.5+ | PDF generation | Utility |
