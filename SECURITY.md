# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |

## Reporting a Vulnerability

Do not include PHI, real DICOM objects, credentials, or private institutional details in a public issue.

Use GitHub private vulnerability reporting when available. If that is not available, open a minimal public issue describing the affected component and request a private follow-up channel.

## Data Handling Expectations

- Run real-data analyses only inside an authorized environment.
- Use synthetic fixtures for demos and automated tests.
- Review generated reports before sharing them outside the authorized environment.
- Treat dose-audit findings as quality-review prompts, not clinical orders or compliance determinations.
