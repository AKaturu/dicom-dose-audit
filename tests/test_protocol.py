from __future__ import annotations

from pathlib import Path

import pytest

from dicom_dose_audit.config import COL_DLP
from dicom_dose_audit.protocol import (
    DoseStudyProtocol,
    load_dose_study_protocol,
    write_dose_study_protocol_template,
)


def test_dose_study_protocol_template_loads(tmp_path: Path) -> None:
    path = write_dose_study_protocol_template(tmp_path / "dose_study_protocol.json")
    protocol = load_dose_study_protocol(path)
    assert protocol.study_id == "dicom-dose-audit-public-ct-v1"
    assert protocol.minimum_studies >= 250
    assert COL_DLP in protocol.dose_metrics
    assert "medical_physicist" in protocol.reviewer_roles


def test_dose_study_protocol_rejects_missing_id() -> None:
    with pytest.raises(ValueError, match="study_id"):
        DoseStudyProtocol(
            study_id="",
            title="Missing ID",
            data_source="TCIA",
            primary_metric="DLP",
            minimum_studies=100,
        )


def test_dose_study_protocol_rejects_invalid_minimum_studies() -> None:
    with pytest.raises(ValueError, match="minimum_studies"):
        DoseStudyProtocol(
            study_id="dose-v1",
            title="Invalid count",
            data_source="TCIA",
            primary_metric="DLP",
            minimum_studies=0,
        )
