"""Orchestration layer for complete CT radiation-dose audit analyses.

Validates data, runs the full audit pipeline (grouping, missing-dose detection,
outlier detection, protocol-version comparison, monthly trends), and provides
output writers that persist results as CSV and JSON.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from .analytics.comparisons import (
    ProtocolComparison,
    compare_protocol_versions,
    comparisons_dataframe,
)
from .analytics.grouping import GroupSummary, group_summary_all_stratifiers, group_summary_dataframe
from .analytics.missing import MissingDoseReport, analyze_missing_dose, missing_dose_dataframe
from .analytics.outliers import OutlierFlag, detect_outliers, outliers_dataframe
from .analytics.trends import MonthlyTrend, monthly_trends, trends_dataframe
from .config import (
    COL_PROTOCOL,
    COL_STUDY_DATE,
    DEFAULT_CONFIDENCE_LEVEL,
)
from .schemas import validate_dataframe


@dataclass(frozen=True)
class DoseAuditResult:
    """Complete audit result bundle shared by CLI, dashboard, and report."""

    dataframe: pd.DataFrame
    group_summaries: list[GroupSummary]
    missing: MissingDoseReport
    outliers: list[OutlierFlag]
    version_comparisons: list[ProtocolComparison]
    trends: list[MonthlyTrend]
    n_studies: int
    n_protocols: int
    n_outliers: int

    @property
    def start_date(self) -> pd.Timestamp:
        return pd.to_datetime(self.dataframe[COL_STUDY_DATE]).min()

    @property
    def end_date(self) -> pd.Timestamp:
        return pd.to_datetime(self.dataframe[COL_STUDY_DATE]).max()


def load_and_validate_csv(path: str | Path) -> pd.DataFrame:
    """Read a dose CSV and validate it against the public contract."""
    return validate_dataframe(pd.read_csv(path))


def load_and_validate_records(records: list[dict[str, object]]) -> pd.DataFrame:
    """Convert parsed records to a DataFrame and validate."""
    return validate_dataframe(pd.DataFrame(records))


def run_dose_audit(
    df: pd.DataFrame,
    *,
    confidence: float = DEFAULT_CONFIDENCE_LEVEL,
    n_bootstrap: int = 1000,
) -> DoseAuditResult:
    """Validate data and run the full dose audit pipeline.

    Parameters
    ----------
    df:
        Raw dose dataframe (from CSV or DICOM ingestion). May contain dates as
        strings; the schema coerces them.
    confidence:
        Confidence level for bootstrap CIs.
    n_bootstrap:
        Number of bootstrap resamples for version comparisons.

    Returns
    -------
    DoseAuditResult with all audit outputs.
    """
    validated = validate_dataframe(df).sort_values(COL_STUDY_DATE).reset_index(drop=True)

    groups = group_summary_all_stratifiers(validated)
    missing = analyze_missing_dose(validated)
    outliers_list = detect_outliers(validated)
    comparisons = compare_protocol_versions(
        validated, confidence=confidence, n_bootstrap=n_bootstrap
    )
    trend_list = monthly_trends(validated)

    return DoseAuditResult(
        dataframe=validated,
        group_summaries=groups,
        missing=missing,
        outliers=outliers_list,
        version_comparisons=comparisons,
        trends=trend_list,
        n_studies=len(validated),
        n_protocols=validated[COL_PROTOCOL].nunique(),
        n_outliers=len(outliers_list),
    )


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def write_audit_outputs(
    result: DoseAuditResult,
    output_dir: str | Path,
) -> dict[str, Path]:
    """Persist audit tables as CSV plus a compact JSON summary."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    outputs = {
        "summary": out / "group_summary.csv",
        "missing": out / "missing_dose.csv",
        "outliers": out / "outliers.csv",
        "versions": out / "protocol_versions.csv",
        "trends": out / "monthly_trends.csv",
        "json": out / "audit_summary.json",
    }
    group_summary_dataframe(result.group_summaries).to_csv(outputs["summary"], index=False)
    missing_dose_dataframe(result.missing).to_csv(outputs["missing"], index=False)
    outliers_dataframe(result.outliers).to_csv(outputs["outliers"], index=False)
    comparisons_dataframe(result.version_comparisons).to_csv(outputs["versions"], index=False)
    trends_dataframe(result.trends).to_csv(outputs["trends"], index=False)
    outputs["json"].write_text(
        json.dumps(audit_summary_dict(result), indent=2),
        encoding="utf-8",
    )
    return outputs


# ---------------------------------------------------------------------------
# Frame helpers for report/dashboard
# ---------------------------------------------------------------------------


def summary_metrics_frame(result: DoseAuditResult) -> pd.DataFrame:
    """Top-line protocol-level summary (grouped by protocol, both metrics)."""
    protocol_groups = [g for g in result.group_summaries if g.stratifier == COL_PROTOCOL]
    return group_summary_dataframe(protocol_groups)


def audit_summary_dict(result: DoseAuditResult) -> dict[str, Any]:
    """Small JSON-serializable summary for automation and CI smoke tests."""
    return {
        "n_studies": result.n_studies,
        "n_protocols": result.n_protocols,
        "n_outliers": result.n_outliers,
        "n_studies_missing_ctdi": result.missing.n_studies_missing_ctdi,
        "n_studies_missing_dlp": result.missing.n_studies_missing_dlp,
        "n_studies_missing_both": result.missing.n_studies_missing_both,
        "start_date": result.start_date.strftime("%Y-%m-%d"),
        "end_date": result.end_date.strftime("%Y-%m-%d"),
        "protocols": sorted(result.dataframe[COL_PROTOCOL].dropna().unique().tolist()),
        "version_comparisons": len(result.version_comparisons),
        "monthly_trend_points": len(result.trends),
    }


def _round(val: float | int | None) -> float | None:
    if val is None:
        return None
    if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
        return None
    return round(float(val), 4)
