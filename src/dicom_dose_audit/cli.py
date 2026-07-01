"""Command-line interface for dicom-dose-audit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .analysis import (
    DoseAuditResult,
    load_and_validate_csv,
    run_dose_audit,
    write_audit_outputs,
)
from .data import write_synthetic_demo_bundle
from .dicom import (
    ingest_dicom_dir,
    records_to_dataframe,
    write_synthetic_dicom_dir,
)
from .protocol import load_dose_study_protocol, write_dose_study_protocol_template
from .report import generate_dose_report

app = typer.Typer(
    name="dicom-dose-audit",
    help="CT radiation-dose audit: read DICOM dose, flag outliers, generate QI reports.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def demo(
    output: Annotated[Path, typer.Option(help="Directory for demo data and reports.")] = Path(
        "outputs/demo"
    ),
    n: Annotated[int, typer.Option(help="Number of synthetic studies.")] = 200,
    seed: Annotated[int, typer.Option(help="Random seed for reproducible data.")] = 42,
    pdf: Annotated[bool, typer.Option("--pdf/--no-pdf", help="Also attempt PDF export.")] = True,
) -> None:
    """Generate synthetic DICOM studies and a complete dose audit report."""
    output.mkdir(parents=True, exist_ok=True)

    # Write synthetic DICOM files to a temp directory, then ingest them.
    dicom_dir = output / "dicom_synthetic"
    specs, ingest_report = write_synthetic_dicom_dir(dicom_dir, n=n, seed=seed)

    console.print(
        f"[green]Wrote {len(specs)} synthetic DICOM studies:[/green] {dicom_dir}"
    )
    console.print(
        f"  {ingest_report.ct_image_records} CT images, "
        f"{ingest_report.rdsr_records} RDSR documents, "
        f"{ingest_report.skipped_unsupported} skipped"
    )

    # Convert parsed records to a validated DataFrame and run audit.
    df = records_to_dataframe(ingest_report.records)
    result = run_dose_audit(df)
    write_audit_outputs(result, output)
    artifacts = generate_dose_report(result, output, include_pdf=pdf)

    console.print(f"[green]Wrote audit outputs to:[/green] {output}")
    console.print(f"[green]Wrote HTML report:[/green] {artifacts.html}")
    if artifacts.pdf:
        console.print(f"[green]Wrote PDF report:[/green] {artifacts.pdf}")
    elif artifacts.pdf_error:
        console.print(f"[yellow]PDF skipped; see:[/yellow] {artifacts.pdf_error}")

    _print_summary_table(result)


@app.command("demo-bundle")
def demo_bundle(
    output: Annotated[
        Path, typer.Option(help="Directory for the shareable synthetic bundle.")
    ] = Path("outputs/synthetic_demo_bundle"),
    n: Annotated[int, typer.Option(help="Number of synthetic studies.")] = 250,
    seed: Annotated[int, typer.Option(help="Random seed for reproducible data.")] = 42,
    start_date: Annotated[
        str, typer.Option(help="First synthetic study date, in YYYY-MM-DD format.")
    ] = "2025-10-01",
    pdf: Annotated[bool, typer.Option("--pdf/--no-pdf", help="Also attempt PDF export.")] = True,
    force: Annotated[
        bool, typer.Option("--force", help="Overwrite an existing non-empty bundle directory.")
    ] = False,
) -> None:
    """Generate a synthetic, shareable report bundle with no DICOM files or PHI."""
    try:
        artifacts = write_synthetic_demo_bundle(
            output,
            n=n,
            seed=seed,
            start_date=start_date,
            include_pdf=pdf,
            force=force,
        )
    except FileExistsError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc

    console.print(f"[green]Wrote synthetic demo bundle:[/green] {output}")
    for name, path in artifacts.items():
        console.print(f"  {name}: {path}")


@app.command("ingest")
def ingest_command(
    dicom_dir: Annotated[Path, typer.Argument(help="Directory containing DICOM files.")],
    output_csv: Annotated[Path, typer.Option("--csv", help="Destination dose CSV path.")] = Path(
        "outputs/ingested_dose_data.csv"
    ),
) -> None:
    """Parse DICOM files from a directory and write a dose CSV."""
    report = ingest_dicom_dir(dicom_dir)
    console.print(
        f"[green]Scanned {report.scanned} files, "
        f"parsed {report.total_records} dose records[/green]"
    )
    if report.skipped_non_dicom:
        console.print(f"  [yellow]{report.skipped_non_dicom} non-DICOM files skipped[/yellow]")
    if report.skipped_unsupported:
        console.print(f"  [yellow]{report.skipped_unsupported} unsupported SOP classes skipped[/yellow]")

    df = records_to_dataframe(report.records)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    console.print(f"[green]Wrote dose CSV:[/green] {output_csv} ({len(df)} rows)")


@app.command()
def compute(
    csv: Annotated[Path, typer.Option("--csv", help="Dose CSV to analyze.")] = Path(
        "outputs/ingested_dose_data.csv"
    ),
    output: Annotated[Path, typer.Option(help="Directory for CSV/JSON outputs.")] = Path(
        "outputs/audit"
    ),
) -> None:
    """Compute dose audit metrics and write machine-readable outputs."""
    df = load_and_validate_csv(csv)
    result = run_dose_audit(df)
    outputs = write_audit_outputs(result, output)
    _print_summary_table(result)
    console.print(f"[green]Wrote outputs to:[/green] {output}")
    for name, path in outputs.items():
        console.print(f"  {name}: {path}")


@app.command("report")
def report_command(
    csv: Annotated[Path, typer.Option("--csv", help="Dose CSV to report on.")] = Path(
        "outputs/ingested_dose_data.csv"
    ),
    output: Annotated[Path, typer.Option(help="Directory for report artifacts.")] = Path(
        "outputs/report"
    ),
    basename: Annotated[str, typer.Option(help="Report filename without extension.")] = (
        "dicom_dose_audit_report"
    ),
    pdf: Annotated[bool, typer.Option("--pdf/--no-pdf", help="Also attempt PDF export.")] = True,
) -> None:
    """Generate a downloadable HTML report and optional PDF."""
    df = load_and_validate_csv(csv)
    result = run_dose_audit(df)
    artifacts = generate_dose_report(result, output, basename=basename, include_pdf=pdf)
    console.print(f"[green]Wrote HTML report:[/green] {artifacts.html}")
    if artifacts.pdf:
        console.print(f"[green]Wrote PDF report:[/green] {artifacts.pdf}")
    elif artifacts.pdf_error:
        console.print(f"[yellow]PDF skipped; see:[/yellow] {artifacts.pdf_error}")


@app.command()
def serve(
    host: Annotated[str, typer.Option(help="Streamlit server host.")] = "localhost",
    port: Annotated[int, typer.Option(help="Streamlit server port.")] = 8501,
) -> None:
    """Launch the Streamlit dashboard."""
    app_path = Path(__file__).parent / "app" / "main.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        host,
        "--server.port",
        str(port),
    ]
    raise typer.Exit(subprocess.run(cmd, check=False).returncode)


@app.command("study-protocol-template")
def study_protocol_template_command(
    output: Annotated[Path, typer.Argument(help="Destination dose study protocol JSON.")],
    force: Annotated[bool, typer.Option("--force", help="Overwrite existing file.")] = False,
) -> None:
    """Write an editable dose audit study protocol template."""
    try:
        path = write_dose_study_protocol_template(output, force=force)
    except FileExistsError as exc:
        raise typer.BadParameter(str(exc)) from exc
    console.print(f"[green]Wrote dose study protocol template:[/green] {path}")


@app.command("study-protocol-validate")
def study_protocol_validate_command(
    protocol: Annotated[Path, typer.Argument(help="Dose study protocol JSON to validate.")],
) -> None:
    """Validate and summarize a dose audit study protocol."""
    loaded = load_dose_study_protocol(protocol)
    console.print(f"[green]Loaded dose study protocol:[/green] {loaded.study_id}")
    console.print(f"  Primary metric: {loaded.primary_metric}")
    console.print(f"  Minimum studies: {loaded.minimum_studies}")
    console.print(f"  Grouping columns: {', '.join(loaded.grouping_columns)}")


def _print_summary_table(result: DoseAuditResult) -> None:
    """Print a top-line summary to the console."""
    table = Table(title="dicom-dose-audit summary")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Studies", str(result.n_studies))
    table.add_row("Protocols", str(result.n_protocols))
    table.add_row("Date range", f"{result.start_date:%Y-%m-%d} to {result.end_date:%Y-%m-%d}")
    table.add_row("Missing CTDIvol", str(result.missing.n_studies_missing_ctdi))
    table.add_row("Missing DLP", str(result.missing.n_studies_missing_dlp))
    table.add_row("Missing both", str(result.missing.n_studies_missing_both))
    table.add_row("Statistical outliers", str(result.n_outliers))
    table.add_row("Protocol version comparisons", str(len(result.version_comparisons)))
    console.print(table)


if __name__ == "__main__":
    app()
