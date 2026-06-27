from __future__ import annotations

import pandas as pd

from dicom_dose_audit.analytics.comparisons import (
    ProtocolComparison,
    compare_protocol_versions,
    comparisons_dataframe,
)
from dicom_dose_audit.config import (
    COL_CTDI_VOL,
    COL_DLP,
    COL_PATIENT_ID,
    COL_PROTOCOL,
    COL_PROTOCOL_VERSION,
    COL_STUDY_DATE,
    COL_STUDY_UID,
)


def test_version_comparison_basic(df_comparison):
    comparisons = compare_protocol_versions(df_comparison)
    assert len(comparisons) >= 2
    for c in comparisons:
        assert c.protocol == "CT Head"
        assert c.version_a in ("v1", "v2")
        assert c.version_b in ("v1", "v2")
        assert c.version_a != c.version_b


def test_version_comparison_direction(df_comparison):
    comparisons = compare_protocol_versions(df_comparison)
    ct_comp = [c for c in comparisons if c.metric == COL_CTDI_VOL]
    if ct_comp:
        c = ct_comp[0]
        assert c.mean_diff is not None
        assert c.median_diff is not None


def test_no_version_column(minimal_df):
    comparisons = compare_protocol_versions(minimal_df)
    assert comparisons == []


def test_single_version_only():
    df = pd.DataFrame(
        {
            COL_STUDY_UID: ["s1", "s2"],
            COL_PATIENT_ID: ["p1", "p2"],
            COL_STUDY_DATE: ["2024-01-01", "2024-01-02"],
            COL_PROTOCOL: ["CT Head", "CT Chest"],
            COL_PROTOCOL_VERSION: ["v1", "v1"],
            COL_CTDI_VOL: [25.0, 30.0],
            COL_DLP: [500.0, 600.0],
        }
    )
    comparisons = compare_protocol_versions(df)
    assert comparisons == []


def test_three_versions():
    rng = __import__("numpy").random.default_rng(42)
    dfs = []
    for i, v in enumerate(["v1", "v2", "v3"]):
        d = pd.DataFrame(
            {
                COL_STUDY_UID: [f"{v}_{j}" for j in range(10)],
                COL_PATIENT_ID: [f"p_{v}_{j}" for j in range(10)],
                COL_STUDY_DATE: pd.date_range("2024-01-01", periods=10, freq="D"),
                COL_PROTOCOL: ["CT Head"] * 10,
                COL_PROTOCOL_VERSION: [v] * 10,
                COL_CTDI_VOL: rng.normal(30 - i * 3, 3, 10),
                COL_DLP: rng.normal(600 - i * 50, 50, 10),
            }
        )
        dfs.append(d)
    df = pd.concat(dfs, ignore_index=True)
    comparisons = compare_protocol_versions(df)
    assert len(comparisons) == 6  # 3 pairs x 2 metrics


def test_small_group_no_ci():
    df = pd.DataFrame(
        {
            COL_STUDY_UID: ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"],
            COL_PATIENT_ID: ["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8", "p9", "p10"],
            COL_STUDY_DATE: pd.date_range("2024-01-01", periods=10, freq="D"),
            COL_PROTOCOL: ["CT Head"] * 10,
            COL_PROTOCOL_VERSION: ["v1"] * 5 + ["v2"] * 5,
            COL_CTDI_VOL: [30, 32, 28, 31, 29, 25, 26, 24, 27, 25],
            COL_DLP: [600, 620, 580, 610, 590, 500, 520, 480, 510, 490],
        }
    )
    comparisons = compare_protocol_versions(df)
    assert len(comparisons) >= 2
    for c in comparisons:
        assert c.ci_lower is not None
        assert c.ci_upper is not None


def test_comparisons_dataframe(df_comparison):
    comparisons = compare_protocol_versions(df_comparison)
    df = comparisons_dataframe(comparisons)
    assert not df.empty
    assert "protocol" in df.columns
    assert "mean_diff" in df.columns


def test_comparisons_dataframe_empty():
    df = comparisons_dataframe([])
    assert df.empty


def test_protocol_comparison_dataclass():
    c = ProtocolComparison(
        protocol="CT Head", version_a="v1", version_b="v2",
        metric=COL_CTDI_VOL, n_a=20, n_b=20,
        mean_a=35.0, mean_b=28.0, median_a=34.5, median_b=27.8,
        mean_diff=-7.0, median_diff=-6.7,
        ci_lower=-10.0, ci_upper=-4.0,
        p_value_mannwhitney=0.001, n_bootstrap=1000,
    )
    assert c.mean_diff == -7.0
    assert c.n_bootstrap == 1000
