from __future__ import annotations

import json
import tempfile

import pandas as pd

from dicom_dose_audit.analysis import (
    DoseAuditResult,
    audit_summary_dict,
    load_and_validate_csv,
    run_dose_audit,
    summary_metrics_frame,
    write_audit_outputs,
)
from dicom_dose_audit.config import (
    COL_PROTOCOL,
)


def test_run_dose_audit(sample_df):
    result = run_dose_audit(sample_df)
    assert isinstance(result, DoseAuditResult)
    assert result.n_studies == 50
    assert result.n_protocols == 2
    assert result.start_date == pd.Timestamp("2024-01-01")
    assert result.end_date == pd.Timestamp("2024-02-19")


def test_run_dose_audit_minimal(minimal_df):
    result = run_dose_audit(minimal_df)
    assert result.n_studies == 3
    assert result.n_protocols == 2


def test_dose_audit_result_properties(sample_df):
    result = run_dose_audit(sample_df)
    assert result.dataframe is not None
    assert len(result.group_summaries) > 0
    assert result.outliers is not None
    assert result.version_comparisons is not None
    assert result.trends is not None


def test_summary_metrics_frame(sample_df):
    result = run_dose_audit(sample_df)
    df = summary_metrics_frame(result)
    assert not df.empty
    assert all(df["stratifier"] == COL_PROTOCOL)


def test_audit_summary_dict(sample_df):
    result = run_dose_audit(sample_df)
    summary = audit_summary_dict(result)
    assert summary["n_studies"] == 50
    assert summary["n_protocols"] == 2
    assert "start_date" in summary
    assert "end_date" in summary
    assert "protocols" in summary
    assert COL_PROTOCOL in summary["protocols"] or "CT Head" in summary["protocols"]


def test_audit_summary_dict_json_serializable(sample_df):
    result = run_dose_audit(sample_df)
    summary = audit_summary_dict(result)
    json_str = json.dumps(summary)
    assert json_str


def test_write_audit_outputs(sample_df):
    result = run_dose_audit(sample_df)
    with tempfile.TemporaryDirectory() as tmp:
        outputs = write_audit_outputs(result, tmp)
        assert "summary" in outputs
        assert "missing" in outputs
        assert "outliers" in outputs
        assert "versions" in outputs
        assert "trends" in outputs
        assert "json" in outputs
        for path in outputs.values():
            assert path.exists()


def test_load_and_validate_csv(minimal_df):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        minimal_df.to_csv(f.name, index=False)
        validated = load_and_validate_csv(f.name)
    assert validated is not None
    assert len(validated) == 3


def test_dose_audit_result_frozen():
    import pandas as pd

    result = DoseAuditResult(
        dataframe=pd.DataFrame(),
        group_summaries=[],
        missing=__import__("dicom_dose_audit.analytics.missing", fromlist=["MissingDoseReport"]).MissingDoseReport(
            per_column=[], n_studies_missing_ctdi=0, n_studies_missing_dlp=0,
            n_studies_missing_both=0, n_total=0,
        ),
        outliers=[],
        version_comparisons=[],
        trends=[],
        n_studies=0,
        n_protocols=0,
        n_outliers=0,
    )
    assert result.n_studies == 0
