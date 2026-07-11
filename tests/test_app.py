from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_streamlit_dashboard_smoke() -> None:
    app_path = (
        Path(__file__).parents[1] / "src" / "dicom_dose_audit" / "app" / "main.py"
    )

    app = AppTest.from_file(str(app_path), default_timeout=60).run()

    assert not app.exception
    assert app.title[0].value == "DICOM Dose Audit"
    assert len(app.metric) == 5
