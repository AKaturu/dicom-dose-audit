from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from dicom_dose_audit.config import (
    COL_CTDI_VOL,
    COL_DLP,
    COL_HAS_DOSE_SR,
    COL_KVP,
    COL_PATIENT_ID,
    COL_PROTOCOL,
    COL_PROTOCOL_VERSION,
    COL_SCAN_LENGTH_CM,
    COL_SCANNER_MANUFACTURER,
    COL_SCANNER_MODEL,
    COL_SITE,
    COL_SIZE_CATEGORY,
    COL_SOURCE,
    COL_STUDY_DATE,
    COL_STUDY_UID,
    COL_TUBE_CURRENT,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 50
    return pd.DataFrame(
        {
            COL_STUDY_UID: [f"study_{i}" for i in range(n)],
            COL_PATIENT_ID: [f"pat_{i}" for i in range(n)],
            COL_STUDY_DATE: pd.date_range("2024-01-01", periods=n, freq="D"),
            COL_PROTOCOL: ["CT Head"] * (n // 2) + ["CT Chest"] * (n // 2),
            COL_CTDI_VOL: rng.uniform(10, 60, n),
            COL_DLP: rng.uniform(200, 1200, n),
            COL_PROTOCOL_VERSION: ["v1"] * (n // 2) + ["v2"] * (n // 2),
            COL_SCANNER_MODEL: ["Discovery CT750"] * n,
            COL_SCANNER_MANUFACTURER: ["GE"] * n,
            COL_SITE: ["Site A"] * n,
            COL_SIZE_CATEGORY: np.random.choice(["medium", "large"], n),
            COL_KVP: [120.0] * n,
            COL_TUBE_CURRENT: rng.uniform(100, 400, n),
            COL_SCAN_LENGTH_CM: rng.uniform(20, 40, n),
            COL_HAS_DOSE_SR: rng.choice([True, False], n),
            COL_SOURCE: ["dicom"] * n,
        }
    )


@pytest.fixture
def minimal_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            COL_STUDY_UID: ["s1", "s2", "s3"],
            COL_PATIENT_ID: ["p1", "p2", "p3"],
            COL_STUDY_DATE: ["2024-01-01", "2024-02-01", "2024-03-01"],
            COL_PROTOCOL: ["CT Head", "CT Head", "CT Chest"],
            COL_CTDI_VOL: [25.0, 30.0, 15.0],
            COL_DLP: [500.0, 600.0, 300.0],
        }
    )


@pytest.fixture
def df_with_missing() -> pd.DataFrame:
    return pd.DataFrame(
        {
            COL_STUDY_UID: ["s1", "s2", "s3", "s4", "s5"],
            COL_PATIENT_ID: ["p1", "p2", "p3", "p4", "p5"],
            COL_STUDY_DATE: pd.date_range("2024-01-01", periods=5, freq="D"),
            COL_PROTOCOL: ["CT Head"] * 5,
            COL_CTDI_VOL: [25.0, None, 30.0, None, 35.0],
            COL_DLP: [500.0, 600.0, None, None, None],
        }
    )


@pytest.fixture
def df_outlier() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    normal = pd.DataFrame(
        {
            COL_STUDY_UID: [f"n_{i}" for i in range(30)],
            COL_PATIENT_ID: [f"np_{i}" for i in range(30)],
            COL_STUDY_DATE: pd.date_range("2024-01-01", periods=30, freq="D"),
            COL_PROTOCOL: ["CT Head"] * 30,
            COL_CTDI_VOL: rng.normal(30, 3, 30),
            COL_DLP: rng.normal(600, 50, 30),
        }
    )
    outliers = pd.DataFrame(
        {
            COL_STUDY_UID: ["out_1", "out_2"],
            COL_PATIENT_ID: ["op_1", "op_2"],
            COL_STUDY_DATE: ["2024-02-01", "2024-02-02"],
            COL_PROTOCOL: ["CT Head", "CT Head"],
            COL_CTDI_VOL: [80.0, 90.0],
            COL_DLP: [1500.0, 1800.0],
        }
    )
    return pd.concat([normal, outliers], ignore_index=True)


@pytest.fixture
def df_comparison() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    v1 = pd.DataFrame(
        {
            COL_STUDY_UID: [f"v1_{i}" for i in range(20)],
            COL_PATIENT_ID: [f"p_{i}" for i in range(20)],
            COL_STUDY_DATE: pd.date_range("2024-01-01", periods=20, freq="D"),
            COL_PROTOCOL: ["CT Head"] * 20,
            COL_PROTOCOL_VERSION: ["v1"] * 20,
            COL_CTDI_VOL: rng.normal(35, 4, 20),
            COL_DLP: rng.normal(700, 60, 20),
        }
    )
    v2 = pd.DataFrame(
        {
            COL_STUDY_UID: [f"v2_{i}" for i in range(20)],
            COL_PATIENT_ID: [f"q_{i}" for i in range(20)],
            COL_STUDY_DATE: pd.date_range("2024-06-01", periods=20, freq="D"),
            COL_PROTOCOL: ["CT Head"] * 20,
            COL_PROTOCOL_VERSION: ["v2"] * 20,
            COL_CTDI_VOL: rng.normal(28, 3, 20),
            COL_DLP: rng.normal(550, 50, 20),
        }
    )
    return pd.concat([v1, v2], ignore_index=True)
