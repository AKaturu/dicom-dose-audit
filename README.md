# DICOM Dose Audit

[![CI](https://github.com/AKaturu/dicom-dose-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/AKaturu/dicom-dose-audit/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Open-source CT radiation-dose audit tooling for quality-improvement and research workflows.

`dicom-dose-audit` reads CTDIvol and DLP values from DICOM metadata or dose structured reports, groups studies by protocol, scanner, and patient-size category, detects missing dose metadata, flags statistical outliers, compares protocol versions, plots monthly trends, and generates quality-improvement reports.

> Research and quality-improvement software only. This project is not a medical device, does not diagnose disease, and does not determine regulatory compliance by itself.

## Highlights

- DICOM CT dose extraction with synthetic data support for demos and tests.
- Protocol, scanner, and size-category grouping.
- Missing-dose metadata summaries.
- Outlier detection and protocol-version comparisons.
- Monthly trend tables and static/interactive plotting helpers.
- HTML report generation for reproducible internal review.
- CLI-first design with reusable Python modules under `src/dicom_dose_audit`.

## Repository Layout

| Path | Purpose |
|---|---|
| `src/dicom_dose_audit/cli.py` | Typer CLI entry point |
| `src/dicom_dose_audit/dicom/` | DICOM reading and synthetic DICOM helpers |
| `src/dicom_dose_audit/analytics/` | Grouping, missingness, trend, outlier, and comparison logic |
| `src/dicom_dose_audit/report/` | HTML report renderer and templates |
| `tests/` | Unit and integration tests for schemas and analytics |
| `docs/REQUIREMENTS.md` | Product requirements and acceptance criteria |
| `docs/RESEARCH.md` | Domain and implementation research notes |

## Quick Start

```bash
git clone https://github.com/AKaturu/dicom-dose-audit.git
cd dicom-dose-audit
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
python -m ruff check .
python -m pytest
```

After installation, the CLI is available as:

```bash
dicom-dose-audit --help
```

## Typical Workflow

1. Export a local, authorized set of CT DICOM objects or dose reports.
2. Run extraction/analysis through the CLI or Python modules.
3. Review missing dose metadata, protocol grouping, outlier flags, and trend summaries.
4. Generate an HTML report for internal physics, quality, or research review.
5. Treat all findings as review prompts that require local clinical and physics governance.

## Dashboard and Desktop Downloads

Run the local dashboard with:

```bash
python -m pip install -e ".[app]"
dicom-dose-audit serve
```

Tagged releases can provide native desktop artifacts for Windows, macOS, and Linux. These launch the dashboard locally in your browser and do not require API keys.

See [docs/DESKTOP_RELEASES.md](docs/DESKTOP_RELEASES.md) for build and release details.

## Testing and Quality

| Check | Command |
|---|---|
| Lint | `python -m ruff check .` |
| Unit/integration tests | `python -m pytest` |
| Package install smoke test | `python -m pip install -e ".[dev]"` |

The GitHub Actions workflow runs linting and tests on Python 3.11 and 3.12.

## Data and Privacy

- Do not commit DICOM files, protected health information, institutional exports, or screenshots containing patient identifiers.
- Use synthetic fixtures for demos, tests, and examples.
- Run real-data analyses only under appropriate institutional approval and data-handling controls.
- Generated reports should be reviewed before being shared outside the local authorized environment.

## Documentation

- [Requirements](docs/REQUIREMENTS.md)
- [Desktop Releases](docs/DESKTOP_RELEASES.md)
- [Roadmap](docs/ROADMAP.md)
- [Research Notes](docs/RESEARCH.md)

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and review expectations.

## Security

Please report security concerns through GitHub private vulnerability reporting when available, or by opening a minimal public issue without PHI or sensitive details. See [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
