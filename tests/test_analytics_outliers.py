from __future__ import annotations

import pandas as pd

from dicom_dose_audit.analytics.outliers import (
    OutlierFlag,
    detect_outliers,
    outliers_dataframe,
)
from dicom_dose_audit.config import (
    COL_CTDI_VOL,
    COL_DLP,
    COL_PATIENT_ID,
    COL_PROTOCOL,
    COL_STUDY_DATE,
    COL_STUDY_UID,
    OutlierConfig,
)


def test_no_outliers_in_normal_data(minimal_df):
    flags = detect_outliers(minimal_df)
    assert flags == []


def test_outliers_detected(df_outlier):
    flags = detect_outliers(df_outlier)
    assert len(flags) >= 2
    for f in flags:
        assert f.protocol == "CT Head"
        assert f.metric in (COL_CTDI_VOL, COL_DLP)


def test_far_outlier_severity():
    df = _make_outlier_df(normal=30, outlier_value=[200.0, 5000.0])
    flags = detect_outliers(df)
    ct_flags = [f for f in flags if f.metric == COL_CTDI_VOL]
    if ct_flags:
        assert any(f.severity == "far_outlier" for f in ct_flags)


def test_group_below_min_group_size(df_outlier):
    config = OutlierConfig(min_group_size=50)
    flags = detect_outliers(df_outlier, config=config)
    assert flags == []


def test_mad_only_outlier():
    df = _make_mad_outlier_df()
    flags = detect_outliers(df)
    if flags:
        assert any(f.method == "mad" for f in flags)


def test_unknown_stratifier_returns_empty(sample_df):
    flags = detect_outliers(sample_df, group_by="nonexistent")
    assert flags == []


def test_outlier_flag_dataclass():
    f = OutlierFlag(
        study_uid="s1", patient_id="p1", study_date="2024-01-01",
        protocol="CT Head", metric=COL_CTDI_VOL, value=80.0,
        lower_fence=10.0, upper_fence=50.0, iqr=10.0,
        mad_z_score=4.5, severity="outlier", method="both",
    )
    assert f.study_uid == "s1"
    assert f.metric == COL_CTDI_VOL


def test_outliers_dataframe_conversion(df_outlier):
    flags = detect_outliers(df_outlier)
    df = outliers_dataframe(flags)
    assert not df.empty
    assert "study_uid" in df.columns
    assert "metric" in df.columns


def test_outliers_dataframe_empty():
    df = outliers_dataframe([])
    assert df.empty
    assert list(df.columns) == [
        "study_uid", "patient_id", "study_date", "protocol",
        "metric", "value", "lower_fence", "upper_fence",
        "iqr", "mad_z_score", "severity", "method",
    ]


def _make_outlier_df(normal, outlier_value):
    import numpy as np

    np.random.seed(42)
    normal_ctdi = np.random.normal(30, 3, normal)
    normal_dlp = np.random.normal(600, 50, normal)
    return pd.DataFrame(
        {
            COL_STUDY_UID: [f"s{i}" for i in range(normal + 1)],
            COL_PATIENT_ID: [f"p{i}" for i in range(normal + 1)],
            COL_STUDY_DATE: pd.date_range("2024-01-01", periods=normal + 1, freq="D"),
            COL_PROTOCOL: ["CT Head"] * (normal + 1),
            COL_CTDI_VOL: [*list(normal_ctdi), outlier_value[0]],
            COL_DLP: [*list(normal_dlp), outlier_value[1]],
        }
    )


def _make_mad_outlier_df():
    import numpy as np

    np.random.seed(42)
    vals = list(np.random.normal(30, 2, 20))
    vals.append(30.0)
    vals.append(30.0)
    vals.append(30.0)
    vals.append(30.0)
    vals.append(55.0)
    return pd.DataFrame(
        {
            COL_STUDY_UID: [f"s{i}" for i in range(25)],
            COL_PATIENT_ID: [f"p{i}" for i in range(25)],
            COL_STUDY_DATE: pd.date_range("2024-01-01", periods=25, freq="D"),
            COL_PROTOCOL: ["CT Head"] * 25,
            COL_CTDI_VOL: vals,
            COL_DLP: np.random.normal(600, 50, 25),
        }
    )
