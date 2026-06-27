from __future__ import annotations

import pandas as pd

from dicom_dose_audit.analytics.trends import (
    MonthlyTrend,
    monthly_trends,
    trends_dataframe,
)
from dicom_dose_audit.config import (
    COL_CTDI_VOL,
    COL_DLP,
    COL_PATIENT_ID,
    COL_PROTOCOL,
    COL_STUDY_DATE,
    COL_STUDY_UID,
)


def test_monthly_trends_basic(sample_df):
    trends = monthly_trends(sample_df)
    assert len(trends) >= 2
    for t in trends:
        assert t.year_month is not None
        assert t.protocol in ("CT Head", "CT Chest")
        assert t.metric in (COL_CTDI_VOL, COL_DLP)
        assert t.n > 0


def test_single_month_single_protocol():
    df = pd.DataFrame(
        {
            COL_STUDY_UID: ["s1", "s2", "s3"],
            COL_PATIENT_ID: ["p1", "p2", "p3"],
            COL_STUDY_DATE: ["2024-01-01", "2024-01-15", "2024-01-30"],
            COL_PROTOCOL: ["CT Head"] * 3,
            COL_CTDI_VOL: [25.0, 30.0, 35.0],
            COL_DLP: [500.0, 600.0, 700.0],
        }
    )
    trends = monthly_trends(df)
    jan_trends = [t for t in trends if t.year_month == "2024-01"]
    assert len(jan_trends) == 2
    head_ctdi = [t for t in jan_trends if t.protocol == "CT Head" and t.metric == COL_CTDI_VOL]
    assert len(head_ctdi) == 1
    assert head_ctdi[0].median == 30.0


def test_all_dose_null():
    df = _make_df(ctdi=[None, None], dlp=[None, None])
    trends = monthly_trends(df)
    for t in trends:
        assert t.median is None


def test_no_date_column():
    df = pd.DataFrame({"protocol": ["CT Head"]})
    trends = monthly_trends(df)
    assert trends == []


def test_no_protocol_column():
    df = pd.DataFrame({COL_STUDY_DATE: ["2024-01-01"], COL_CTDI_VOL: [25.0]})
    trends = monthly_trends(df)
    assert trends == []


def test_trends_sorted(sample_df):
    trends = monthly_trends(sample_df)
    keys = [(t.year_month, t.protocol, t.metric) for t in trends]
    assert keys == sorted(keys)


def test_trends_dataframe(sample_df):
    trends = monthly_trends(sample_df)
    df = trends_dataframe(trends)
    assert not df.empty
    assert list(df.columns)[:3] == ["year_month", "protocol", "metric"]


def test_trends_dataframe_empty():
    df = trends_dataframe([])
    assert df.empty


def test_monthly_trend_dataclass():
    t = MonthlyTrend(
        year_month="2024-01", protocol="CT Head",
        metric=COL_CTDI_VOL, n=10, median=30.0,
        p25=25.0, p75=35.0, mean=31.0,
    )
    assert t.year_month == "2024-01"
    assert t.median == 30.0


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
