"""PyInstaller desktop launcher for dicom-dose-audit."""

from __future__ import annotations

import os
import sys
import threading
import webbrowser
from pathlib import Path


def _app_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "dicom_dose_audit" / "app" / "main.py"  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1] / "src" / "dicom_dose_audit" / "app" / "main.py"


def main() -> int:
    app_path = _app_path()
    if "--self-check" in sys.argv:
        import dicom_dose_audit  # noqa: F401

        if not app_path.exists():
            print(f"Missing dashboard app: {app_path}", file=sys.stderr)
            return 1
        print("dicom-dose-audit desktop launcher OK")
        return 0

    from streamlit.web import cli as stcli

    port = os.environ.get("DICOM_DOSE_AUDIT_PORT", "8501")
    url = f"http://localhost:{port}"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        "localhost",
        "--server.port",
        port,
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    return int(stcli.main() or 0)


if __name__ == "__main__":
    raise SystemExit(main())
