from __future__ import annotations

import json

import pandas as pd
from typer.testing import CliRunner

from dicom_dose_audit.cli import app
from dicom_dose_audit.data import write_synthetic_demo_bundle


def test_write_synthetic_demo_bundle_outputs_shareable_artifacts(tmp_path):
    bundle = tmp_path / "bundle"
    artifacts = write_synthetic_demo_bundle(bundle, n=40, seed=7, include_pdf=False)

    expected = {
        "readme",
        "manifest",
        "screenshot_guide",
        "synthetic_csv",
        "report_html",
        "analysis_json",
        "analysis_summary",
    }
    assert expected.issubset(artifacts)
    for path in artifacts.values():
        assert path.exists()

    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["bundle_type"] == "synthetic_demo"
    assert manifest["synthetic"] is True
    assert manifest["contains_phi"] is False
    assert manifest["contains_dicom"] is False
    assert manifest["parameters"]["n"] == 40
    assert manifest["parameters"]["seed"] == 7
    assert manifest["summary"]["n_studies"] == 40
    assert manifest["files"]["synthetic_csv"] == "data/synthetic_dose_data.csv"

    csv = pd.read_csv(bundle / "data" / "synthetic_dose_data.csv")
    assert set(csv["source"].unique()) == {"synthetic"}
    assert len(csv) == 40

    readme = (bundle / "README.md").read_text(encoding="utf-8")
    assert "no PHI" in readme
    assert "not evidence of clinical safety" in readme


def test_write_synthetic_demo_bundle_refuses_existing_directory(tmp_path):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "keep.txt").write_text("existing", encoding="utf-8")

    try:
        write_synthetic_demo_bundle(bundle, include_pdf=False)
    except FileExistsError as exc:
        assert "already contains files" in str(exc)
    else:
        raise AssertionError("expected FileExistsError")


def test_demo_bundle_cli(tmp_path):
    runner = CliRunner()
    bundle = tmp_path / "cli-bundle"

    result = runner.invoke(
        app,
        [
            "demo-bundle",
            "--output",
            str(bundle),
            "--n",
            "24",
            "--seed",
            "3",
            "--no-pdf",
        ],
    )

    assert result.exit_code == 0
    assert "Wrote synthetic demo bundle" in result.output
    assert (bundle / "manifest.json").exists()
    assert (bundle / "report" / "synthetic_dicom_dose_audit_report.html").exists()
