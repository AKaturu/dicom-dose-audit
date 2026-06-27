from __future__ import annotations

import pandas as pd

from dicom_dose_audit.analytics.missing import (
    ColumnMissingness,
    MissingDoseReport,
    analyze_missing_dose,
    missing_dose_dataframe,
)
from dicom_dose_audit.config import (
    COL_CTDI_VOL,
    COL_DLP,
    COL_PATIENT_ID,
    COL_PROTOCOL,
    COL_STUDY_DATE,
    COL_STUDY_UID,
)


def test_all_dose_present(minimal_df):
    report = analyze_missing_dose(minimal_df)
    assert report.n_total == 3
    assert report.n_studies_missing_ctdi == 0
    assert report.n_studies_missing_dlp == 0
    assert report.n_studies_missing_both == 0
    for col in report.per_column:
        assert col.n_missing == 0


def test_all_dose_missing():
    df = _make_df(ctdi=[None, None, None], dlp=[None, None, None])
    report = analyze_missing_dose(df)
    assert report.n_total == 3
    assert report.n_studies_missing_ctdi == 3
    assert report.n_studies_missing_dlp == 3
    assert report.n_studies_missing_both == 3
    for col in report.per_column:
        assert col.n_missing == 3
        assert col.pct_missing == 1.0


def test_partial_missing(df_with_missing):
    report = analyze_missing_dose(df_with_missing)
    assert report.n_total == 5
    assert report.n_studies_missing_ctdi == 2
    assert report.n_studies_missing_dlp == 3
    assert report.n_studies_missing_both == 1


def test_empty_dataframe():
    df = pd.DataFrame(columns=[COL_STUDY_UID, COL_PATIENT_ID, COL_STUDY_DATE, COL_PROTOCOL, COL_CTDI_VOL, COL_DLP])
    report = analyze_missing_dose(df)
    assert report.n_total == 0
    assert report.n_studies_missing_ctdi == 0
    assert report.n_studies_missing_dlp == 0


def test_missing_columns_treated_as_all_missing():
    df = pd.DataFrame(
        {
            COL_STUDY_UID: ["s1", "s2"],
            COL_PATIENT_ID: ["p1", "p2"],
            COL_STUDY_DATE: ["2024-01-01", "2024-01-02"],
            COL_PROTOCOL: ["CT Head", "CT Head"],
        }
    )
    report = analyze_missing_dose(df)
    for col in report.per_column:
        assert col.n_missing == 2


def test_column_missingness_dataclass():
    cm = ColumnMissingness(column=COL_CTDI_VOL, n_missing=5, n_total=100, pct_missing=0.05)
    assert cm.column == COL_CTDI_VOL
    assert cm.n_missing == 5
    assert cm.n_total == 100


def test_missing_dose_report_dataclass():
    cm = ColumnMissingness(column=COL_CTDI_VOL, n_missing=1, n_total=10, pct_missing=0.1)
    report = MissingDoseReport(
        per_column=[cm],
        n_studies_missing_ctdi=1,
        n_studies_missing_dlp=2,
        n_studies_missing_both=0,
        n_total=10,
    )
    assert report.n_studies_missing_both == 0
    assert len(report.per_column) == 1


def test_missing_dose_dataframe(minimal_df):
    report = analyze_missing_dose(minimal_df)
    df = missing_dose_dataframe(report)
    assert list(df.columns) == ["column", "n_missing", "n_total", "pct_missing"]
    assert len(df) == 2


def test_missing_dose_dataframe_empty():
    cm = ColumnMissingness(column=COL_CTDI_VOL, n_missing=0, n_total=0, pct_missing=0.0)
    report = MissingDoseReport(
        per_column=[cm],
        n_studies_missing_ctdi=0,
        n_studies_missing_dlp=0,
        n_studies_missing_both=0,
        n_total=0,
    )
    df = missing_dose_dataframe(report)
    assert len(df) == 1


def _make_df(ctdi, dlp):
    return pd.DataFrame(
        {
            COL_STUDY_UID: [f"s{i}" for i in range(len(ctdi))],
            COL_PATIENT_ID: [f"p{i}" for i in range(len(ctdi))],
            COL_STUDY_DATE: pd.date_range("2024-01-01", periods=len(ctdi), freq="D"),
            COL_PROTOCOL: ["CT Head"] * len(ctdi),
            COL_CTDI_VOL: ctdi,
            COL_DLP: dlp,
        }
    )
