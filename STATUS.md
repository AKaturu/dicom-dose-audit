# Status

## Current Release
**v0.1.0** (2026-06-28) — MVP release.

## Implemented Features
- DICOM CT dose extraction (CTDIvol, DLP) from metadata and dose structured reports
- Synthetic DICOM data generation for demos and tests (no PHI exposure)
- Protocol, scanner, and size-category grouping with descriptive statistics
- Missing-dose metadata detection and reporting
- Statistical outlier detection (IQR-based) with configurable thresholds
- Protocol-version comparison (CTDIvol and DLP per protocol across time periods)
- Monthly trend tables with static (matplotlib) and interactive (plotly) plotting
- HTML report generation with optional PDF export (WeasyPrint + fpdf2 fallback)
- Streamlit dashboard with data upload, summary views, and trend exploration
- Synthetic demo bundle generation for screenshots, docs, and examples
- Native desktop release packaging (Windows, macOS, Linux)

## Validation Status
- **Unit tests**: Pass (schema validation, analytics, reporting)
- **Synthetic end-to-end test**: Complete (demo bundle generates synthetic DICOM objects, runs extraction, produces report)
- **Public-data evaluation**: Not completed
- **Expert review**: Not completed
- **Institutional validation**: Not completed
- **Prospective clinical validation**: Not completed

## Planned Work
- Validation against institutional CT dose index registry exports
- Expanded modality support (CBCT, mammography, fluoroscopy)
- DICOM Structured Report parser enhancements for SR IOD variants
- Configurable DRL (diagnostic reference level) comparison
- Native release distribution and PyPI publishing
