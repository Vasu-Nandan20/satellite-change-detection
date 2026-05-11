# Contributing to SENTINEL

Thank you for your interest in contributing to the SENTINEL Satellite Change Detection System! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/satellite-change-detection.git
   cd satellite-change-detection
   ```
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # macOS/Linux
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development Setup

### Prerequisites
- Python 3.10+
- pip package manager
- Git

### Running the Application
```bash
python app.py
```

### Running Tests
```bash
python -m pytest tests/ -v
```

## Project Structure

```
satellite-change-detection/
├── app.py                    # Entry point
├── engine/                   # Computer Vision pipeline
│   ├── alignment.py          # Image registration (ORB/SIFT/ECC)
│   ├── detector.py           # Change detection (AbsDiff/SSIM/Combined)
│   ├── classifier.py         # Change type classification
│   └── analyzer.py           # Statistics and heatmap generation
├── gui/                      # CustomTkinter GUI
│   ├── app_window.py         # Main window and navigation
│   ├── dashboard_frame.py    # Dashboard tab
│   ├── detection_frame.py    # Detection workflow tab
│   ├── analytics_frame.py    # Analytics charts tab
│   ├── history_frame.py      # History log tab
│   └── settings_frame.py     # Settings tab
├── utils/                    # Utilities
│   ├── image_utils.py        # Image conversion helpers
│   └── report_generator.py   # PDF/CSV report generation
└── docs/                     # Documentation
```

## How to Contribute

### Reporting Bugs
- Use the [Bug Report](https://github.com/Vasu-Nandan20/satellite-change-detection/issues/new?template=bug_report.md) template
- Include steps to reproduce, expected vs actual behavior, and screenshots

### Suggesting Features
- Use the [Feature Request](https://github.com/Vasu-Nandan20/satellite-change-detection/issues/new?template=feature_request.md) template
- Describe the use case and proposed solution

### Code Contributions

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Test thoroughly
4. Submit a Pull Request

## Coding Standards

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Type Hints**: Add type hints where possible
- **Comments**: Write clear, concise comments for complex logic
- **Naming**: Use `snake_case` for functions/variables, `PascalCase` for classes

### Example

```python
def detect_changes(img_before: np.ndarray, img_after: np.ndarray) -> tuple:
    """Detect changes between two aligned satellite images.

    Args:
        img_before: BGR reference image.
        img_after: BGR target image (aligned).

    Returns:
        Tuple of (contours, binary_mask, raw_difference_map).
    """
    ...
```

## Commit Guidelines

Use conventional commit messages:

```
feat: add SIFT alignment method
fix: resolve heatmap color scaling issue
docs: update README with architecture diagram
refactor: extract image loading into utility module
test: add unit tests for classifier
chore: update dependencies in requirements.txt
```

## Pull Request Process

1. Update documentation if needed
2. Ensure all existing features still work
3. Add a clear description of changes
4. Reference related issues using `#issue-number`
5. Request review from maintainers

---

Thank you for contributing! 🛰️
