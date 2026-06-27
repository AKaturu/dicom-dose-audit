# Contributing

Thanks for helping improve DICOM Dose Audit. Keep contributions small, reviewable, and free of patient data.

## Development Setup

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Before Opening a Pull Request

Run:

```bash
python -m ruff check .
python -m pytest
```

## Contribution Rules

- Do not commit DICOM studies, PHI, credentials, institutional exports, or private reports.
- Prefer synthetic data for tests and examples.
- Add or update tests for behavioral changes.
- Update documentation when user-facing commands, outputs, or assumptions change.
- Keep clinical, regulatory, and compliance claims conservative and evidence-bound.

## Review Scope

Maintainers will prioritize correctness, privacy, reproducibility, and clear quality-improvement boundaries.
