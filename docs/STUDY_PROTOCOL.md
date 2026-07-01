# Dose Audit Study Protocol Workflow

Use a locked study protocol before analyzing public CT collections, institutional DICOM exports, or CT Radiation Dose SR data. The protocol records the dose metrics, grouping plan, minimum sample sizes, benchmark sources, and review roles that should be fixed before results are inspected.

## Create a Template

```bash
dicom-dose-audit study-protocol-template dose_study_protocol.json
```

Edit the placeholders before analysis:

- `study_id` and `title`
- public or institutional `data_source`
- primary dose metric and statistical methods
- minimum study count and minimum studies per protocol
- grouping columns
- benchmark/diagnostic-reference-level sources
- medical-physics and radiology/QI reviewer roles
- protocol lock date and registration URL

## Validate Before Analysis

```bash
dicom-dose-audit study-protocol-validate dose_study_protocol.json
```

Archive the protocol SHA-256 with the final analysis outputs. If benchmark sources or inclusion criteria change after results are inspected, create a new protocol version and document the reason.

## Publication Guardrails

- Statistical outliers are QI review targets, not determinations that studies were clinically unsafe.
- Diagnostic reference levels are advisory optimization benchmarks, not regulatory limits.
- Institutional and public-data analyses require qualified medical-physics review before clinical interpretation.
- Do not commit DICOM files, PHI, institutional exports, or local machine paths.
- This project is research/QI software and is not a medical device.
