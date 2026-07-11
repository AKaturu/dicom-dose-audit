from importlib.metadata import version

from dicom_dose_audit import __version__


def test_package_version_matches_distribution_metadata() -> None:
    assert __version__ == version("dicom-dose-audit")
