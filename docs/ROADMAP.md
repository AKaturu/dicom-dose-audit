# Roadmap

This roadmap tracks planned work after the initial public MVP. Items are grouped by release value rather than promised dates.

## Near Term

- Publish cross-platform desktop downloads for Windows, macOS, and Linux through GitHub Actions release artifacts.
- [Implemented] Add a fully synthetic demo report bundle with screenshots that can be shared without DICOM privacy risk.
- Expand dashboard workflows for CSV upload, synthetic examples, report download, and outlier review.
- Add regression fixtures for malformed DICOM headers, missing dose metadata, unsupported SOP classes, and empty study groups.

## Dose Audit Analytics

- Add configurable local protocol reference levels and warning thresholds.
- Add scanner/protocol control-chart views for longitudinal quality-improvement review.
- Add additional patient-size normalization options where source metadata supports them.
- Add cohort filters for site, scanner, protocol, date range, and source type.

## DICOM Support

- Expand CT Radiation Dose Structured Report extraction coverage with additional real-world fixture patterns.
- Add clearer unsupported-transfer-syntax and missing-pixel-data diagnostics.
- Add optional anonymized DICOM fixture generation for new edge cases.
- Document known vendor-specific limitations without embedding private institutional data.

## Review Workflow

- Add reviewed/unreviewed status for outlier flags.
- Capture reviewer, disposition, and follow-up notes in a local CSV/JSON review file.
- Add report sections that separate automated flags from reviewed findings.
- Add export packaging for physics or quality-improvement committee review.

## Release Hardening

- [Implemented] Sign or checksum release artifacts when the project starts publishing tagged releases.
- Add packaged desktop smoke tests in CI.
- Add accessibility and responsive-layout checks for the dashboard.
- Publish versioned documentation pages once the command and CSV contracts stabilize.

## Out of Scope

- Diagnosing disease.
- Replacing medical physics review.
- Certifying Joint Commission, ACR, CMS, state, or local regulatory compliance.
- Sharing protected health information or real DICOM examples in the public repository.
