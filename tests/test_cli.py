from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

import dicom_dose_audit.cli as cli
from dicom_dose_audit.data import generate_synthetic_dose_csv
from dicom_dose_audit.dicom import write_synthetic_dicom_dir

runner = CliRunner()


@pytest.fixture
def synthetic_csv(tmp_path: Path) -> Path:
    path = tmp_path / "dose.csv"
    generate_synthetic_dose_csv(path, n=20, seed=9)
    return path


def test_demo_command_runs_end_to_end(tmp_path: Path) -> None:
    output = tmp_path / "demo"
    result = runner.invoke(
        cli.app,
        ["demo", "--output", str(output), "--n", "8", "--seed", "4", "--no-pdf"],
    )

    assert result.exit_code == 0, result.output
    assert (output / "dicom_dose_audit_report.html").is_file()


def test_ingest_command_writes_csv(tmp_path: Path) -> None:
    dicom_dir = tmp_path / "dicom"
    write_synthetic_dicom_dir(dicom_dir, n=4, seed=2)
    output_csv = tmp_path / "ingested.csv"

    result = runner.invoke(cli.app, ["ingest", str(dicom_dir), "--csv", str(output_csv)])

    assert result.exit_code == 0, result.output
    assert output_csv.is_file()


def test_compute_command_writes_machine_readable_outputs(
    synthetic_csv: Path,
    tmp_path: Path,
) -> None:
    output = tmp_path / "analysis"
    result = runner.invoke(
        cli.app,
        ["compute", "--csv", str(synthetic_csv), "--output", str(output)],
    )

    assert result.exit_code == 0, result.output
    assert (output / "audit_summary.json").is_file()


def test_report_command_writes_html(synthetic_csv: Path, tmp_path: Path) -> None:
    output = tmp_path / "report"
    result = runner.invoke(
        cli.app,
        [
            "report",
            "--csv",
            str(synthetic_csv),
            "--output",
            str(output),
            "--basename",
            "review",
            "--no-pdf",
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output / "review.html").is_file()


def test_study_protocol_template_and_validate_commands(tmp_path: Path) -> None:
    protocol = tmp_path / "protocol.json"
    created = runner.invoke(cli.app, ["study-protocol-template", str(protocol)])
    validated = runner.invoke(cli.app, ["study-protocol-validate", str(protocol)])

    assert created.exit_code == 0, created.output
    assert validated.exit_code == 0, validated.output
    assert "Loaded dose study protocol" in validated.output


def test_serve_command_constructs_streamlit_process(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], *, check: bool):
        assert check is False
        calls.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    result = runner.invoke(cli.app, ["serve", "--host", "127.0.0.1", "--port", "8765"])

    assert result.exit_code == 0, result.output
    assert calls and calls[0][-4:] == ["--server.address", "127.0.0.1", "--server.port", "8765"]
