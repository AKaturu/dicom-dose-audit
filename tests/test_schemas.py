from __future__ import annotations

import pandas as pd
import pandera.errors
import pytest

from dicom_dose_audit.config import COL_CTDI_VOL, COL_DLP, COL_STUDY_DATE
from dicom_dose_audit.schemas import SCHEMA, validate_dataframe


def test_valid_minimal_dataframe(minimal_df):
    validated = validate_dataframe(minimal_df)
    assert COL_STUDY_DATE in validated.columns
    assert validated[COL_STUDY_DATE].dtype == "datetime64[ns]"


def test_valid_full_dataframe(sample_df):
    validated = validate_dataframe(sample_df)
    assert len(validated) == 50


def test_missing_required_column():
    df = pd.DataFrame({"study_uid": ["s1"], "patient_id": ["p1"], COL_STUDY_DATE: ["2024-01-01"]})
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_dataframe(df)


def test_empty_study_uid():
    df = pd.DataFrame(
        {
            "study_uid": [""],
            "patient_id": ["p1"],
            COL_STUDY_DATE: ["2024-01-01"],
            "protocol": ["CT Head"],
            COL_CTDI_VOL: [25.0],
            COL_DLP: [500.0],
        }
    )
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_dataframe(df)


def test_negative_ctdi_vol():
    df = _minimal([-1.0, 500.0])
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_dataframe(df)


def test_negative_dlp():
    df = _minimal([25.0, -100.0])
    with pytest.raises(pandera.errors.SchemaErrors):
        validate_dataframe(df)


def test_null_ctdi_allowed():
    df = _minimal([None, 500.0])
    validated = validate_dataframe(df)
    assert validated[COL_CTDI_VOL].isna().iloc[0]


def test_null_dlp_allowed():
    df = _minimal([25.0, None])
    validated = validate_dataframe(df)
    assert validated[COL_DLP].isna().iloc[0]


def test_extra_columns_tolerated(minimal_df):
    minimal_df["extra_column"] = "test"
    validated = validate_dataframe(minimal_df)
    assert "extra_column" in validated.columns


def test_study_date_coercion():
    df = _minimal([25.0, 500.0])
    df[COL_STUDY_DATE] = ["2024/01/01"]
    validated = validate_dataframe(df)
    assert validated[COL_STUDY_DATE].dtype == "datetime64[ns]"


def test_schema_reusable(minimal_df):
    validated = SCHEMA.validate(minimal_df, lazy=True)
    assert len(validated) == 3


def _minimal(dose_row):
    return pd.DataFrame(
        {
            "study_uid": ["s1"],
            "patient_id": ["p1"],
            COL_STUDY_DATE: ["2024-01-01"],
            "protocol": ["CT Head"],
            COL_CTDI_VOL: [dose_row[0]],
            COL_DLP: [dose_row[1]],
        }
    )
