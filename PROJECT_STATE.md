# PROJECT_STATE

## Current Status

GitHub presentation polish, dashboard restoration, roadmap, and native desktop release scaffolding completed for the public repository.

## Completed This Session

- Replaced the placeholder README with a complete GitHub-facing overview.
- Added CI for Python 3.11 and 3.12.
- Added contribution and security documentation.
- Updated package metadata, project URLs, and MIT license credit to Abinav Katuru.
- Added `docs/ROADMAP.md` and `docs/DESKTOP_RELEASES.md`.
- Added a Streamlit dashboard at `src/dicom_dose_audit/app/main.py`, which fixes the existing `dicom-dose-audit serve` command target.
- Added PyInstaller desktop packaging and a GitHub Actions workflow for Windows ZIP, macOS DMG, and Linux tar.gz artifacts.

## Validation

Run before release:

```bash
python -m ruff check .
python -m pytest
python -m pip install -e ".[app,packaging]"
python scripts/build_native.py --help
```

GitHub Actions should run the same checks on each push and pull request to `main`.

## Remaining Work

- Add screenshots or report examples after a fully synthetic demo artifact is generated.
- Cut a version tag such as `v0.1.0` to trigger the native desktop release workflow and attach artifacts to a GitHub Release.
- Publish release notes once the first tagged release is cut.
