"""Synthetic dose-data generation for tests and the demo CSV path.

Generates a validated dose CSV directly (no DICOM serialization) from the same
underlying study specs that :mod:`dicom_dose_audit.dicom.synthetic` uses. This
is the fast path for ``demo`` and unit tests that do not need to exercise the
DICOM round-trip.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import DEFAULT_SIZE_CATEGORY
from ..dicom.synthetic import generate_synthetic_study_specs
from ..schemas import validate_dataframe


def generate_synthetic_dose_csv(
    path: str | Path,
    n: int = 200,
    *,
    seed: int = 42,
    start_date: str = "2025-10-01",
) -> pd.DataFrame:
    """Generate a validated dose CSV with planted quality issues.

    Parameters
    ----------
    path:
        Destination CSV path.
    n:
        Number of synthetic studies.
    seed:
        Random seed for reproducibility.
    start_date:
        First study date (YYYY-MM-DD).

    Returns
    -------
    Validated dose dataframe.
    """
    specs = generate_synthetic_study_specs(n=n, seed=seed, start_date=start_date)
    rows: list[dict[str, object]] = []
    for s in specs:
        rows.append(
            {
                "study_uid": str(s["study_uid"]),
                "patient_id": str(s["patient_id"]),
                "study_date": str(s["study_date"]),
                "protocol": str(s["protocol"]),
                "protocol_version": str(s["protocol_version"]) if s.get("protocol_version") else None,
                "scanner_model": str(s["scanner_model"]) if s.get("scanner_model") else None,
                "site": str(s["site"]) if s.get("site") else None,
                "size_category": str(s.get("size_category") or DEFAULT_SIZE_CATEGORY),
                "ctdi_vol_mgy": s["ctdi_vol"] if s["ctdi_vol"] is not None else None,
                "dlp_mgy_cm": s["dlp"] if s["dlp"] is not None else None,
                "kvp": float(s["kvp"]) if s.get("kvp") is not None else None,
                "tube_current_ma": float(s["tube_current"]) if s.get("tube_current") is not None else None,
                "scan_length_cm": float(s["scan_length_cm"]) if s.get("scan_length_cm") is not None else None,
                "has_dose_sr": s.get("source_kind") == "rdsr",
                "source": "synthetic",
            }
        )

    df = pd.DataFrame(rows)
    validated = validate_dataframe(df)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    validated.to_csv(destination, index=False)
    return validated
