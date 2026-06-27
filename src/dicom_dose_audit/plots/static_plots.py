"""Static matplotlib plots for the dose audit report.

Produces boxplots (dose by protocol, dose by scanner) and monthly trend line
plots (median CTDIvol and DLP per protocol per month). All figures are
returned as base-64 data-URI PNG strings for embedding in the HTML report,
or written to BytesIO buffers for the PDF fallback.
"""

from __future__ import annotations

import base64
import io

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ..config import COL_CTDI_VOL, COL_PROTOCOL, COL_SCANNER_MODEL

# Shared color palette (matches the sibling project).
BLUE = "#1769aa"
GREEN = "#1f7a4d"
ORANGE = "#b54d12"
MUTED = "#64707d"


def figure_to_data_uri() -> str:
    """Render the current matplotlib figure to a base-64 data-URI PNG string."""
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close()
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def figure_to_bytes(buf: io.BytesIO) -> None:
    """Write the current matplotlib figure to a BytesIO buffer."""
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=160, bbox_inches="tight")
    plt.close()
    buf.seek(0)


def boxplot_by_protocol(df: pd.DataFrame, metric: str = COL_CTDI_VOL) -> str:
    """Boxplot of a dose metric grouped by protocol.

    Returns a base-64 data-URI PNG string.
    """
    if df.empty or COL_PROTOCOL not in df.columns or metric not in df.columns:
        return ""
    vals = pd.to_numeric(df[metric], errors="coerce").dropna()
    if vals.empty:
        return ""

    protocols = sorted(df[COL_PROTOCOL].dropna().unique())
    data = [pd.to_numeric(df.loc[df[COL_PROTOCOL] == p, metric], errors="coerce").dropna() for p in protocols]
    data = [d for d in data if len(d) > 0]

    _, ax = plt.subplots(figsize=(max(6, len(protocols) * 0.9), 4.5))
    ax.boxplot(data, tick_labels=protocols, patch_artist=True, vert=True)
    for patch in ax.patches:  # type: ignore[union-attr]
        patch.set_facecolor(BLUE)
        patch.set_alpha(0.7)
    metric_label = "CTDIvol (mGy)" if metric == COL_CTDI_VOL else "DLP (mGy*cm)"
    ax.set_ylabel(metric_label)
    ax.set_title(f"{metric_label} by Protocol")
    ax.tick_params(axis="x", rotation=30)
    return figure_to_data_uri()


def boxplot_by_scanner(df: pd.DataFrame, metric: str = COL_CTDI_VOL) -> str:
    """Boxplot of a dose metric grouped by scanner model."""
    if df.empty or COL_SCANNER_MODEL not in df.columns or metric not in df.columns:
        return ""
    vals = pd.to_numeric(df[metric], errors="coerce").dropna()
    if vals.empty:
        return ""

    scanners = sorted(df[COL_SCANNER_MODEL].dropna().unique())
    data = [
        pd.to_numeric(df.loc[df[COL_SCANNER_MODEL] == s, metric], errors="coerce").dropna()
        for s in scanners
    ]
    data = [d for d in data if len(d) > 0]

    _, ax = plt.subplots(figsize=(max(6, len(scanners) * 0.9), 4.5))
    ax.boxplot(data, tick_labels=scanners, patch_artist=True, vert=True)
    for patch in ax.patches:  # type: ignore[union-attr]
        patch.set_facecolor(GREEN)
        patch.set_alpha(0.7)
    metric_label = "CTDIvol (mGy)" if metric == COL_CTDI_VOL else "DLP (mGy*cm)"
    ax.set_ylabel(metric_label)
    ax.set_title(f"{metric_label} by Scanner")
    ax.tick_params(axis="x", rotation=30)
    return figure_to_data_uri()


def monthly_trend_plot(trend_df: pd.DataFrame, metric: str = COL_CTDI_VOL) -> str:
    """Monthly median trend plot per protocol for one dose metric.

    Parameters
    ----------
    trend_df:
        The output of ``trends_dataframe()`` — must have columns year_month,
        protocol, metric, median, n.
    metric:
        Which dose metric to plot.
    """
    if trend_df.empty:
        return ""
    sub = trend_df[trend_df["metric"] == metric].copy()
    if sub.empty:
        return ""

    protocols = sorted(sub["protocol"].unique())
    n_months = sub["year_month"].nunique()
    _, ax = plt.subplots(figsize=(max(7, n_months * 0.5), 4.0))
    colors = [BLUE, GREEN, ORANGE, "#7b3294", "#d95f02", "#1b9e77"]
    for i, protocol in enumerate(protocols):
        p_data = sub[sub["protocol"] == protocol].sort_values("year_month")
        ax.plot(
            p_data["year_month"],
            p_data["median"],
            marker="o",
            color=colors[i % len(colors)],
            linewidth=2.0,
            markersize=4,
            label=protocol,
        )
    metric_label = "CTDIvol (mGy)" if metric == COL_CTDI_VOL else "DLP (mGy*cm)"
    ax.set_ylabel(f"Median {metric_label}")
    ax.set_title(f"Monthly Median {metric_label}")
    ax.legend(loc="best", fontsize=8)
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    return figure_to_data_uri()
