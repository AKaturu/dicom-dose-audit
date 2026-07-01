"""Study protocol helpers for CT dose audit publication and QI workflows."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .config import (
    COL_CTDI_VOL,
    COL_DLP,
    COL_PROTOCOL,
    COL_SCANNER_MANUFACTURER,
    COL_SCANNER_MODEL,
    COL_SITE,
    COL_SIZE_CATEGORY,
    DEFAULT_MIN_GROUP_SIZE,
)

DEFAULT_DOSE_METRICS: tuple[str, ...] = (COL_CTDI_VOL, COL_DLP)
DEFAULT_GROUPING: tuple[str, ...] = (
    COL_PROTOCOL,
    COL_SCANNER_MODEL,
    COL_SCANNER_MANUFACTURER,
    COL_SITE,
    COL_SIZE_CATEGORY,
)
DEFAULT_STATISTICAL_METHODS: tuple[str, ...] = (
    "missingness_summary",
    "iqr_outlier_fences",
    "mad_z_score_crosscheck",
    "protocol_version_comparison",
    "monthly_trend_summary",
)


@dataclass(frozen=True)
class DoseStudyProtocol:
    """Locked analysis plan for a dose audit or external validation study."""

    study_id: str
    title: str
    data_source: str
    primary_metric: str
    minimum_studies: int
    minimum_per_protocol: int = DEFAULT_MIN_GROUP_SIZE
    dose_metrics: tuple[str, ...] = DEFAULT_DOSE_METRICS
    grouping_columns: tuple[str, ...] = DEFAULT_GROUPING
    statistical_methods: tuple[str, ...] = DEFAULT_STATISTICAL_METHODS
    benchmark_sources: tuple[str, ...] = ("local diagnostic reference levels",)
    reviewer_roles: tuple[str, ...] = ("medical_physicist", "radiologist_or_qi_lead")
    locked_at: str = ""
    registration_url: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        required = {
            "study_id": self.study_id,
            "title": self.title,
            "data_source": self.data_source,
            "primary_metric": self.primary_metric,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"Dose study protocol missing required fields: {', '.join(missing)}")
        if self.minimum_studies < 1:
            raise ValueError("minimum_studies must be positive")
        if self.minimum_per_protocol < 1:
            raise ValueError("minimum_per_protocol must be positive")
        if not self.dose_metrics:
            raise ValueError("at least one dose metric is required")
        if not self.grouping_columns:
            raise ValueError("at least one grouping column is required")
        if not self.statistical_methods:
            raise ValueError("at least one statistical method is required")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema_version"] = 1
        return payload


def dose_study_protocol_from_dict(data: dict[str, Any]) -> DoseStudyProtocol:
    """Build a validated dose study protocol from JSON-compatible data."""
    return DoseStudyProtocol(
        study_id=str(data.get("study_id", "")),
        title=str(data.get("title", "")),
        data_source=str(data.get("data_source", "")),
        primary_metric=str(data.get("primary_metric", "")),
        minimum_studies=int(data.get("minimum_studies", 0)),
        minimum_per_protocol=int(data.get("minimum_per_protocol", DEFAULT_MIN_GROUP_SIZE)),
        dose_metrics=tuple(data.get("dose_metrics", DEFAULT_DOSE_METRICS)),
        grouping_columns=tuple(data.get("grouping_columns", DEFAULT_GROUPING)),
        statistical_methods=tuple(data.get("statistical_methods", DEFAULT_STATISTICAL_METHODS)),
        benchmark_sources=tuple(data.get("benchmark_sources", ())),
        reviewer_roles=tuple(data.get("reviewer_roles", ())),
        locked_at=str(data.get("locked_at", "")),
        registration_url=str(data.get("registration_url", "")),
        notes=str(data.get("notes", "")),
    )


def load_dose_study_protocol(path: str | Path) -> DoseStudyProtocol:
    """Load and validate a dose study protocol JSON file."""
    return dose_study_protocol_from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def save_dose_study_protocol(protocol: DoseStudyProtocol, path: str | Path) -> Path:
    """Write a dose study protocol JSON file."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(protocol.to_dict(), indent=2) + "\n", encoding="utf-8")
    return destination


def write_dose_study_protocol_template(path: str | Path, *, force: bool = False) -> Path:
    """Write an editable dose audit protocol template."""
    destination = Path(path)
    if destination.exists() and not force:
        raise FileExistsError(f"Refusing to overwrite existing dose study protocol: {destination}")
    protocol = DoseStudyProtocol(
        study_id="dicom-dose-audit-public-ct-v1",
        title="External CT dose-index audit using DICOM dose metadata",
        data_source="TCIA CT collection or governed institutional CT/RDSR export",
        primary_metric="protocol-stratified DLP outlier rate with missing-dose sensitivity analysis",
        minimum_studies=250,
        locked_at="YYYY-MM-DD",
        registration_url="https://osf.io/<placeholder>",
        notes=(
            "Replace placeholders, define benchmark sources before analysis, and archive this "
            "file's SHA-256 with the final evidence package."
        ),
    )
    return save_dose_study_protocol(protocol, destination)
