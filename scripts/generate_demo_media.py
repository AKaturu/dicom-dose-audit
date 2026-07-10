"""Generate GitHub demo media from the synthetic DICOM dose-audit bundle."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "outputs" / "demo-media"
ASSETS = ROOT / "docs" / "assets"
WIDTH = 1280
HEIGHT = 720


def _load_font(size: int, *, mono: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        [
            Path("C:/Windows/Fonts/consola.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
        ]
        if mono
        else [
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


FONT_TITLE = _load_font(44)
FONT_H2 = _load_font(28)
FONT_SMALL = _load_font(18)
FONT_MONO = _load_font(21, mono=True)


def _run_demo(workspace: Path) -> str:
    if workspace.exists():
        shutil.rmtree(workspace)
    cmd = [
        sys.executable,
        "-m",
        "dicom_dose_audit.cli",
        "demo-bundle",
        "--output",
        str(workspace),
        "--n",
        "120",
        "--seed",
        "20260628",
        "--start-date",
        "2026-01-01",
        "--no-pdf",
        "--force",
    ]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                part for part in (str(ROOT / "src"), os.environ.get("PYTHONPATH")) if part
            ),
        },
    )
    return completed.stdout.strip()


def _rounded(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    outline: str | None = None,
) -> None:
    draw.rounded_rectangle(box, radius=8, fill=fill, outline=outline, width=1 if outline else 0)


def _text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    font: ImageFont.ImageFont,
    fill: str = "#f8fafc",
) -> None:
    draw.text(xy, value, font=font, fill=fill)


def _metric(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    label: str,
    value: str,
    color: str,
    *,
    active: bool,
) -> None:
    _rounded(
        draw,
        (x, y, x + 245, y + 105),
        "#17314d" if active else "#101826",
        color if active else "#263244",
    )
    _text(draw, (x + 20, y + 18), label, FONT_SMALL, "#a7b4c8")
    _text(draw, (x + 20, y + 48), value, FONT_H2, color)


def _draw_terminal(draw: ImageDraw.ImageDraw, step: int) -> None:
    _rounded(draw, (62, 180, 690, 640), "#08111f", "#20304b")
    _text(draw, (86, 205), "$ dicom-dose-audit demo-bundle --no-pdf", FONT_MONO, "#80cbc4")
    lines = [
        "Wrote synthetic demo bundle",
        "manifest.json with reproducibility metadata",
        "data/synthetic_dose_data.csv",
        "analysis/audit_summary.json",
        "analysis/group_summary.csv",
        "analysis/outliers.csv",
        "report/synthetic_dicom_dose_audit_report.html",
        "",
        "Safe for GitHub screenshots and release demos",
    ]
    visible_lines = (3, 6, len(lines))[step]
    y = 252
    for line in lines[:visible_lines]:
        short = line if len(line) < 58 else line[:55] + "..."
        _text(draw, (86, y), short, FONT_MONO, "#d5dde8")
        y += 29


def _draw_protocol_bars(draw: ImageDraw.ImageDraw, protocols: list[str], *, active: bool) -> None:
    _rounded(
        draw,
        (730, 432, 1218, 640),
        "#17314d" if active else "#101826",
        "#38bdf8" if active else "#263244",
    )
    _text(draw, (756, 457), "Protocol coverage", FONT_H2, "#f8fafc")
    colors = ["#38bdf8", "#34d399", "#fbbf24", "#f87171"]
    y = 508
    for index, protocol in enumerate(protocols):
        width = 210 - index * 20
        draw.rectangle((756, y, 756 + width, y + 18), fill=colors[index % len(colors)])
        _text(draw, (990, y - 2), protocol, FONT_SMALL, "#cbd5e1")
        y += 34


def _frame(summary: dict[str, Any], output: str, step: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#0b1020")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 92), fill="#111827")
    _text(draw, (60, 26), "DICOM Dose Audit", FONT_TITLE)
    walkthrough_steps = (
        "1/3 Generate a reproducible synthetic CT dose bundle",
        "2/3 Review dose-metadata gaps and statistical outliers",
        "3/3 Compare protocol coverage before report review",
    )
    _text(draw, (60, 105), walkthrough_steps[step], FONT_H2, "#cbd5e1")
    _text(
        draw,
        (60, 144),
        "No DICOM files, no PHI, no clinical or regulatory determinations.",
        FONT_SMALL,
        "#94a3b8",
    )

    _draw_terminal(draw, step)
    _metric(draw, 730, 180, "Studies", str(summary["n_studies"]), "#38bdf8", active=step == 0)
    _metric(draw, 990, 180, "Protocols", str(summary["n_protocols"]), "#34d399", active=step == 2)
    _metric(
        draw,
        730,
        300,
        "Missing CTDI/DLP",
        str(summary["n_studies_missing_both"]),
        "#fbbf24",
        active=step == 1,
    )
    _metric(
        draw, 990, 300, "Outliers flagged", str(summary["n_outliers"]), "#f87171", active=step == 1
    )
    _draw_protocol_bars(draw, list(summary["protocols"]), active=step == 2)
    return image


def _write_media(frames: list[Image.Image]) -> None:
    import imageio.v2 as imageio
    import numpy as np

    ASSETS.mkdir(parents=True, exist_ok=True)
    poster = ASSETS / "demo-poster.png"
    gif = ASSETS / "demo.gif"
    mp4 = ASSETS / "demo.mp4"
    frames[0].save(poster, optimize=True)
    imageio.mimsave(gif, frames, duration=3.0, loop=0)
    with imageio.get_writer(
        mp4, fps=6, codec="libx264", quality=8, macro_block_size=None
    ) as writer:
        for frame in frames:
            for _ in range(18):
                writer.append_data(np.asarray(frame))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=WORKSPACE)
    args = parser.parse_args()

    output = _run_demo(args.workspace)
    manifest = json.loads((args.workspace / "manifest.json").read_text(encoding="utf-8"))
    frames = [_frame(manifest["summary"], output, step) for step in range(3)]
    _write_media(frames)
    print(f"Wrote {ASSETS / 'demo-poster.png'}")
    print(f"Wrote {ASSETS / 'demo.gif'}")
    print(f"Wrote {ASSETS / 'demo.mp4'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
