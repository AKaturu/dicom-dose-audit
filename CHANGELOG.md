# Changelog

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
