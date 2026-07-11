from __future__ import annotations

import base64

import pandas as pd

from dicom_dose_audit.analysis import run_dose_audit
from dicom_dose_audit.analytics.trends import trends_dataframe
from dicom_dose_audit.config import COL_CTDI_VOL
from dicom_dose_audit.plots import boxplot_by_protocol, boxplot_by_scanner, monthly_trend_plot


def _assert_png_data_uri(value: str) -> None:
    prefix = "data:image/png;base64,"
    assert value.startswith(prefix)
    assert base64.b64decode(value.removeprefix(prefix)).startswith(b"\x89PNG\r\n\x1a\n")


def test_protocol_and_scanner_plots_are_valid_pngs(sample_df) -> None:
    _assert_png_data_uri(boxplot_by_protocol(sample_df))
    _assert_png_data_uri(boxplot_by_scanner(sample_df))


def test_boxplot_omits_groups_with_only_missing_metric_values(sample_df) -> None:
    partial = sample_df.copy()
    first_protocol = partial["protocol"].iloc[0]
    partial.loc[partial["protocol"] == first_protocol, "dlp_mgy_cm"] = None

    _assert_png_data_uri(boxplot_by_protocol(partial, "dlp_mgy_cm"))


def test_monthly_trend_plot_is_valid_png(sample_df) -> None:
    result = run_dose_audit(sample_df, n_bootstrap=25)
    trends = trends_dataframe(result.trends)

    _assert_png_data_uri(monthly_trend_plot(trends, COL_CTDI_VOL))


def test_plot_functions_return_empty_string_for_missing_data() -> None:
    assert boxplot_by_protocol(pd.DataFrame()) == ""
    assert boxplot_by_scanner(pd.DataFrame()) == ""
    assert monthly_trend_plot(pd.DataFrame()) == ""
