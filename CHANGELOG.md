# Changelog

## Unreleased

### Fixed
- Correct DICOM RDSR concept mappings and DLP-weighted multi-event CTDIvol aggregation
- Read standard SR `MeasuredValueSequence` values and normalize supported UCUM units
- Preserve scanner manufacturer in synthetic CSV output
- Render escaped dataframe values as functional HTML report tables
- Fall back safely when only part of the DejaVu font family is installed
- Load packaged report templates explicitly as UTF-8

### Changed
- Make WeasyPrint an optional `pdf` extra; fpdf2 remains the portable default fallback
- Publish PEP 561 typing metadata, test on Python 3.13, and modernize SPDX package metadata

## 0.1.0 - 2026-06-28

### Added
- DICOM CT dose extraction (CTDIvol, DLP) from metadata and dose structured reports
- Synthetic DICOM data generation for demos and tests
- Protocol, scanner, and size-category grouping with descriptive statistics
- Missing-dose metadata detection and reporting
- Statistical outlier detection (IQR-based) with configurable thresholds
- Protocol-version comparison (CTDIvol and DLP per protocol across time periods)
- Monthly trend tables with static (matplotlib) and interactive (plotly) plotting
- HTML report with optional PDF export (WeasyPrint + fpdf2 fallback)
- Streamlit dashboard with data upload, summary views, and trend exploration
- Synthetic demo bundle generation for screenshots and examples
- Native desktop release packaging (Windows, macOS, Linux)
- GitHub Actions CI (lint, test)
- Full test suite (schema validation, analytics)
- Reproducible README demo media generation
