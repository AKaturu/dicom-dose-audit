from __future__ import annotations

from pathlib import Path

from dicom_dose_audit.analysis import run_dose_audit
from dicom_dose_audit.report import generate as report_generate
from dicom_dose_audit.report import generate_dose_report, render_report_html


class _RecordingPdf:
    def __init__(self) -> None:
        self.fonts: list[tuple[str, str, str, bool]] = []

    def add_font(self, family: str, style: str, path: str, *, uni: bool) -> None:
        self.fonts.append((family, style, path, uni))


def test_render_report_contains_tables_and_escapes_dataframe_values(sample_df) -> None:
    malicious = sample_df.copy()
    malicious.loc[malicious.index[0], "protocol"] = '<script>alert("dose")</script>'

    html = render_report_html(run_dose_audit(malicious, n_bootstrap=25))

    assert '<table class="dataframe data-table">' in html
    assert "<script>alert" not in html
    assert "&lt;script&gt;alert" in html


def test_generate_html_report_without_optional_pdf(sample_df, tmp_path: Path) -> None:
    artifacts = generate_dose_report(sample_df, tmp_path, include_pdf=False)

    assert artifacts.html.is_file()
    assert artifacts.pdf is None
    assert artifacts.pdf_error is None


def test_pdf_generation_falls_back_when_weasyprint_is_unavailable(
    sample_df,
    tmp_path: Path,
    monkeypatch,
) -> None:
    def fail_weasyprint(*_args, **_kwargs) -> None:
        raise ImportError("optional dependency unavailable")

    def write_fallback(_result, path: Path) -> None:
        path.write_bytes(b"%PDF-fallback")

    monkeypatch.setattr(report_generate, "_write_pdf_weasyprint", fail_weasyprint)
    monkeypatch.setattr(report_generate, "_write_pdf_fpdf2", write_fallback)

    artifacts = generate_dose_report(sample_df, tmp_path, include_pdf=True)

    assert artifacts.pdf is not None
    assert artifacts.pdf.read_bytes() == b"%PDF-fallback"
    assert artifacts.pdf_error is None


def test_font_registration_falls_back_for_incomplete_family(
    tmp_path: Path,
    monkeypatch,
) -> None:
    regular = tmp_path / "DejaVuSans.ttf"
    regular.write_bytes(b"font")
    monkeypatch.setattr(report_generate, "_find_dejavu_sans", lambda: regular)
    pdf = _RecordingPdf()

    assert report_generate._register_fonts(pdf) == "Helvetica"
    assert pdf.fonts == []


def test_font_registration_uses_all_complete_variants(tmp_path: Path, monkeypatch) -> None:
    names = (
        "DejaVuSans.ttf",
        "DejaVuSans-Bold.ttf",
        "DejaVuSans-Oblique.ttf",
        "DejaVuSans-BoldOblique.ttf",
    )
    for name in names:
        (tmp_path / name).write_bytes(b"font")
    regular = tmp_path / "DejaVuSans.ttf"
    monkeypatch.setattr(report_generate, "_find_dejavu_sans", lambda: regular)
    pdf = _RecordingPdf()

    assert report_generate._register_fonts(pdf) == "DejaVu"
    assert [style for _, style, _, _ in pdf.fonts] == ["", "B", "I", "BI"]
