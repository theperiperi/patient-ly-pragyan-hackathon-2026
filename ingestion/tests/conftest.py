"""Shared fixtures for tests."""

import os
import pytest
from pathlib import Path


@pytest.fixture
def sample_data_dir():
    return Path(__file__).parent.parent / "sample_data"


def _first_match(sample_data_dir: Path, pattern: str) -> str:
    """Find the first file matching a glob pattern under sample_data, or skip."""
    matches = sorted(sample_data_dir.glob(pattern))
    if not matches:
        pytest.skip(f"No file matching {pattern} — run the generator first")
    return str(matches[0])


@pytest.fixture
def ehr_admission(sample_data_dir):
    return _first_match(sample_data_dir, "*/ehr/sim_admission.hl7")


@pytest.fixture
def ehr_lab(sample_data_dir):
    return _first_match(sample_data_dir, "*/ehr/sim_lab_results.hl7")


@pytest.fixture
def apple_health(sample_data_dir):
    return _first_match(sample_data_dir, "*/wearables/sim_apple_health.xml")


@pytest.fixture
def google_fit(sample_data_dir):
    return _first_match(sample_data_dir, "*/wearables/sim_google_fit.json")


@pytest.fixture
def ambulance_xml(sample_data_dir):
    return _first_match(sample_data_dir, "*/ambulance/sim_ems_run.xml")


@pytest.fixture
def bedside_json(sample_data_dir):
    return _first_match(sample_data_dir, "*/realtime_vitals/sim_bedside_stream.json")


@pytest.fixture
def ecg_csv(sample_data_dir):
    return _first_match(sample_data_dir, "*/realtime_vitals/sim_ecg_waveform.csv")


@pytest.fixture
def dicom_file(sample_data_dir):
    return _first_match(sample_data_dir, "*/scans_labs/sim_chest_xray.dcm")


@pytest.fixture
def pdf_lab(sample_data_dir):
    return _first_match(sample_data_dir, "*/scans_labs/sim_lab_report.pdf")


@pytest.fixture
def handwritten_note(sample_data_dir):
    return _first_match(sample_data_dir, "*/handwritten/sim_clinical_note.png")
