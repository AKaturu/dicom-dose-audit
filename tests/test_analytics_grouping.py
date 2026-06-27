from __future__ import annotations

import pandas as pd

from dicom_dose_audit.analytics.grouping import (
    group_summary,
    group_summary_all_stratifiers,
    group_summary_dataframe,
)
from dicom_dose_audit.config import (
    COL_CTDI_VOL,
    COL_DLP,
    COL_PROTOCOL,
    COL_SCANNER_MANUFACTURER,
)


def test_group_summary_basic(sample_df):
    results = group_summary(sample_df, stratifier=COL_PROTOCOL, metric=COL_CTDI_VOL)
    assert len(results) == 2
    head = next(r for r in results if r.level == "CT Head")
    assert head.n == 25
    assert head.missing == 0
    assert head.mean is not None
    assert head.median is not None


def test_group_summary_with_missing(df_with_missing):
    results = group_summary(df_with_missing, stratifier=COL_PROTOCOL, metric=COL_CTDI_VOL)
    assert len(results) == 1
    r = results[0]
    assert r.n == 5
    assert r.missing == 2


def test_group_summary_std_none_for_single_row():
    df = _single_row_df()
    results = group_summary(df, stratifier=COL_PROTOCOL, metric=COL_CTDI_VOL)
    assert results[0].std is None


def test_group_summary_empty_for_missing_stratifier(sample_df):
    results = group_summary(sample_df, stratifier="nonexistent", metric=COL_CTDI_VOL)
    assert results == []


def test_group_summary_empty_for_missing_metric(sample_df):
    results = group_summary(sample_df, stratifier=COL_PROTOCOL, metric="nonexistent")
    assert results == []


def test_group_summary_all_stratifiers(sample_df):
    results = group_summary_all_stratifiers(sample_df)
    stratifiers = {r.stratifier for r in results}
    assert COL_PROTOCOL in stratifiers
    assert COL_SCANNER_MANUFACTURER in stratifiers
    assert all(r.metric in (COL_CTDI_VOL, COL_DLP) for r in results)


def test_group_summary_dataframe(sample_df):
    results = group_summary(sample_df, stratifier=COL_PROTOCOL, metric=COL_CTDI_VOL)
    df = group_summary_dataframe(results)
    assert list(df.columns[:3]) == ["stratifier", "level", "metric"]
    assert len(df) == 2


def test_group_summary_dataframe_empty():
    df = group_summary_dataframe([])
    assert df.empty


def test_group_summary_metrics_both(sample_df):
    for metric in (COL_CTDI_VOL, COL_DLP):
        results = group_summary(sample_df, stratifier=COL_PROTOCOL, metric=metric)
        assert len(results) == 2
        r = results[0]
        assert r.metric == metric


def _single_row_df():
    from dicom_dose_audit.config import COL_PATIENT_ID, COL_STUDY_DATE, COL_STUDY_UID

    return pd.DataFrame(
        {
            COL_STUDY_UID: ["s1"],
            COL_PATIENT_ID: ["p1"],
            COL_STUDY_DATE: ["2024-01-01"],
            COL_PROTOCOL: ["CT Head"],
            COL_CTDI_VOL: [25.0],
            COL_DLP: [500.0],
        }
    )
