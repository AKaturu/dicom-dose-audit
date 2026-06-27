"""Streamlit dashboard for dicom-dose-audit."""

from __future__ import annotations

import io
import tempfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dicom_dose_audit.analysis import (
    run_dose_audit,
    summary_metrics_frame,
)
from dicom_dose_audit.analytics.comparisons import comparisons_dataframe
from dicom_dose_audit.analytics.missing import missing_dose_dataframe
from dicom_dose_audit.analytics.outliers import outliers_dataframe
from dicom_dose_audit.analytics.trends import trends_dataframe
from dicom_dose_audit.config import COL_CTDI_VOL, COL_DLP, COL_PROTOCOL
from dicom_dose_audit.data.synthetic import generate_synthetic_dose_csv
from dicom_dose_audit.report import render_report_html

st.set_page_config(page_title="DICOM Dose Audit", layout="wide")


@st.cache_data(show_spinner=False)
def _synthetic(n: int, seed: int) -> pd.DataFrame:
    path = Path(tempfile.gettempdir()) / f"dicom-dose-audit-synthetic-{n}-{seed}.csv"
    return generate_synthetic_dose_csv(path, n=n, seed=seed)


@st.cache_data(show_spinner=False)
def _analyze(csv_bytes: bytes | None, n: int, seed: int):
    df = _synthetic(n, seed) if csv_bytes is None else pd.read_csv(io.BytesIO(csv_bytes))
    return run_dose_audit(df, n_bootstrap=250)


def _box_figure(df: pd.DataFrame, metric: str):
    return px.box(
        df,
        x=COL_PROTOCOL,
        y=metric,
        color=COL_PROTOCOL,
        points="outliers",
        title=f"{metric} by protocol",
    )


def _trend_figure(trend_df: pd.DataFrame, metric: str):
    sub = trend_df[trend_df["metric"] == metric].copy()
    if sub.empty:
        return None
    return px.line(
        sub,
        x="year_month",
        y="median",
        color="protocol",
        markers=True,
        title=f"Monthly median {metric}",
    )


st.sidebar.title("DICOM Dose Audit")
mode = st.sidebar.radio("Data", ["Synthetic demo", "Upload CSV"])
n = st.sidebar.slider("Synthetic studies", 50, 1000, 250, 50)
seed = st.sidebar.number_input("Seed", min_value=0, max_value=100000, value=42, step=1)
uploaded_bytes: bytes | None = None
if mode == "Upload CSV":
    uploaded = st.sidebar.file_uploader("Dose CSV", type=["csv"])
    if uploaded is not None:
        uploaded_bytes = uploaded.getvalue()
    else:
        st.sidebar.info("Using synthetic data until a CSV is uploaded.")

result = _analyze(uploaded_bytes, int(n), int(seed))
summary = summary_metrics_frame(result)
missing = missing_dose_dataframe(result.missing)
outliers = outliers_dataframe(result.outliers)
versions = comparisons_dataframe(result.version_comparisons)
trends = trends_dataframe(result.trends)

st.title("DICOM Dose Audit")
st.caption("Local CT dose metadata audit for quality-improvement and research workflows.")

metric_cols = st.columns(5)
metric_cols[0].metric("Studies", f"{result.n_studies:,}")
metric_cols[1].metric("Protocols", f"{result.n_protocols:,}")
metric_cols[2].metric("Outliers", f"{result.n_outliers:,}")
metric_cols[3].metric("Missing CTDIvol", f"{result.missing.n_studies_missing_ctdi:,}")
metric_cols[4].metric("Missing DLP", f"{result.missing.n_studies_missing_dlp:,}")

overview, trends_tab, outlier_tab, missing_tab, versions_tab, report_tab = st.tabs(
    ["Overview", "Trends", "Outliers", "Missing Dose", "Versions", "Report"]
)

with overview:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(_box_figure(result.dataframe, COL_CTDI_VOL), width="stretch")
    with right:
        st.plotly_chart(_box_figure(result.dataframe, COL_DLP), width="stretch")
    st.dataframe(summary, width="stretch", hide_index=True)

with trends_tab:
    ctdi_trend = _trend_figure(trends, COL_CTDI_VOL)
    dlp_trend = _trend_figure(trends, COL_DLP)
    if ctdi_trend is not None:
        st.plotly_chart(ctdi_trend, width="stretch")
    if dlp_trend is not None:
        st.plotly_chart(dlp_trend, width="stretch")
    st.dataframe(trends, width="stretch", hide_index=True)

with outlier_tab:
    if outliers.empty:
        st.success("No statistical outliers flagged.")
    else:
        st.warning(f"{len(outliers)} statistical outlier rows flagged for review.")
        st.dataframe(outliers, width="stretch", hide_index=True)

with missing_tab:
    st.dataframe(missing, width="stretch", hide_index=True)

with versions_tab:
    if versions.empty:
        st.info("No protocol-version comparisons were available.")
    else:
        st.dataframe(versions, width="stretch", hide_index=True)

with report_tab:
    html = render_report_html(result)
    st.download_button(
        "Download HTML Report",
        html,
        file_name="dicom_dose_audit_report.html",
        mime="text/html",
    )
    st.download_button(
        "Download Analyzed CSV",
        result.dataframe.to_csv(index=False),
        file_name="validated_dose_data.csv",
        mime="text/csv",
    )
