# Changelog

All notable changes to the SENTINEL project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-05-10

### Added
- **Modern GUI** — Complete rewrite using CustomTkinter with dark/light theme support
- **Sidebar Navigation** — 5-tab interface: Dashboard, Detection, Analytics, History, Settings
- **SIFT Alignment** — Scale-Invariant Feature Transform for high-accuracy registration
- **ECC Alignment** — Enhanced Correlation Coefficient for sub-pixel precision
- **SSIM Detection** — Structural Similarity Index for perceptual change detection
- **Combined Detection** — Union of AbsDiff and SSIM for maximum coverage
- **AI Classification** — Automatic change-type classification using HSV color analysis and contour geometry
  - Construction, Vegetation Change, Water Change, Demolition, Other
- **Heatmap Visualization** — JET colormap overlay with Gaussian blur smoothing
- **Change Density Grid** — 8×8 grid analysis showing change concentration per cell
- **Analytics Dashboard** — 4 embedded matplotlib charts (area histogram, type pie, density grid, confidence plot)
- **PDF Report Generation** — Multi-page professional reports with ReportLab
- **CSV Export** — Structured data export with classification labels and confidence scores
- **Image Export** — Save annotated results or heatmaps as PNG/JPG
- **Detection History** — Scrollable table of past analysis sessions from CSV log
- **Settings Panel** — Appearance mode, color theme, UI scaling, default parameters
- **Sensitivity Slider** — Fine-tuned threshold control (1-100)
- **Minimum Area Filter** — Configurable contour area filter to remove noise
- **Progress Bar** — Real-time progress tracking during detection pipeline
- **6 View Modes** — Annotated, Heatmap, Before, After, Mask, Side-by-Side
- **Threaded Processing** — Background thread for detection to keep UI responsive

### Changed
- Upgraded from `opencv-python` to `opencv-contrib-python` for SIFT/SURF support
- Improved ORB alignment with RANSAC refinement and inlier ratio scoring
- Enhanced morphological cleaning with multi-stage open/close operations
- Migrated image display from `cv2.imshow` popups to embedded CTkImage widgets

### Technical Details
- **Architecture**: Modular MVC pattern with separate engine, GUI, and utility packages
- **Files**: 15+ Python modules across 4 packages
- **Dependencies**: 8 libraries (OpenCV, scikit-image, scikit-learn, matplotlib, CustomTkinter, ReportLab, Pillow, NumPy)

## [1.0.0] - 2025-06-15

### Added
- Initial release with basic tkinter GUI (3 buttons)
- ORB-based image alignment with homography
- Absolute difference change detection with fixed threshold
- Bounding box visualization using `cv2.imshow`
- CSV logging of detected change coordinates
- Timestamp overlay on result images
