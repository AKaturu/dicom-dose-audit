"""dicom-dose-audit: open-source CT radiation-dose audit tool.

Read CTDIvol and DLP from DICOM image headers or CT Radiation Dose Structured
Reports (RDSR), group studies by protocol / scanner / patient-size category,
detect missing dose metadata, flag statistical outliers, compare protocol
versions, plot monthly trends, and generate quality-improvement reports.
"""

from __future__ import annotations

from .analysis import DoseAuditResult as DoseAuditResult
from .analysis import run_dose_audit as run_dose_audit
from .analysis import write_audit_outputs as write_audit_outputs

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "DoseAuditResult",
    "run_dose_audit",
    "write_audit_outputs",
]
