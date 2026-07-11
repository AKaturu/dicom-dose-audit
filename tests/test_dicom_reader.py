from __future__ import annotations

import pytest
from pydicom.uid import generate_uid

from dicom_dose_audit.config import (
    CODE_CT_ACQUISITION,
    CODE_DLP,
    CODE_MEAN_CTDI_VOL,
    CODE_SCANNED_LENGTH,
)
from dicom_dose_audit.dicom.reader import read_dicom_dose
from dicom_dose_audit.dicom.synthetic import build_ct_image_dataset, build_rdsr_dataset


def test_ct_image_reader_extracts_metadata_and_leaves_dlp_missing() -> None:
    dataset = build_ct_image_dataset(
        study_uid=generate_uid(),
        patient_id="SYNTH-1",
        study_date="2026-01-02",
        protocol="CT Chest",
        ctdi_vol=8.5,
        scanner_model="GE Revolution",
    )

    record = read_dicom_dose(dataset)

    assert record is not None
    assert record.ctdi_vol == pytest.approx(8.5)
    assert record.dlp is None
    assert record.scanner_manufacturer == "GE"
    assert record.has_dose_sr is False


def test_rdsr_reader_pairs_event_values_for_dlp_weighted_ctdi() -> None:
    dataset = build_rdsr_dataset(
        study_uid=generate_uid(),
        patient_id="SYNTH-2",
        study_date="2026-01-02",
        protocol="CT Abdomen/Pelvis",
        scanner_model="Siemens SOMATOM",
        events=[
            {"ctdi_vol": 10.0, "dlp": 100.0, "scan_length": 20.0},
            {"ctdi_vol": 30.0, "dlp": 300.0, "scan_length": 40.0},
        ],
    )

    record = read_dicom_dose(dataset)

    assert record is not None
    assert record.ctdi_vol == pytest.approx(25.0)
    assert record.dlp == pytest.approx(400.0)
    assert record.scan_length_cm == pytest.approx(60.0)
    assert record.scanner_manufacturer == "Siemens"
    assert record.has_dose_sr is True


def test_synthetic_rdsr_uses_standard_event_codes_and_num_encoding() -> None:
    dataset = build_rdsr_dataset(
        study_uid=generate_uid(),
        patient_id="SYNTH-3",
        study_date="2026-01-02",
        protocol="CT Head",
        scanner_model="Canon Aquilion",
        events=[{"ctdi_vol": 40.0, "dlp": 800.0, "scan_length": 20.0}],
    )

    event = dataset.ContentSequence[0]
    assert event.ConceptNameCodeSequence[0].CodeValue == CODE_CT_ACQUISITION
    scan_length = event.ContentSequence[0]
    assert scan_length.ConceptNameCodeSequence[0].CodeValue == CODE_SCANNED_LENGTH
    assert float(scan_length.MeasuredValueSequence[0].NumericValue) == pytest.approx(200.0)
    dose_items = event.ContentSequence[1].ContentSequence
    assert [item.ConceptNameCodeSequence[0].CodeValue for item in dose_items] == [
        CODE_MEAN_CTDI_VOL,
        CODE_DLP,
    ]
