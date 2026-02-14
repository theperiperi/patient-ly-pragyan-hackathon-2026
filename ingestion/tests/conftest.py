"""Shared fixtures for tests."""

import os
import pytest
from pathlib import Path


@pytest.fixture
def sample_data_dir():
    return Path(__file__).parent.parent / "sample_data"


@pytest.fixture
def ehr_admission(sample_data_dir):
    return str(sample_data_dir / "ehr" / "admission_msg_001.hl7")


@pytest.fixture
def ehr_lab(sample_data_dir):
    return str(sample_data_dir / "ehr" / "lab_result_msg_001.hl7")


@pytest.fixture
def ehr_priya(sample_data_dir):
    return str(sample_data_dir / "ehr" / "admission_priya_002.hl7")


@pytest.fixture
def apple_health(sample_data_dir):
    return str(sample_data_dir / "wearables" / "apple_health_export.xml")


@pytest.fixture
def google_fit(sample_data_dir):
    return str(sample_data_dir / "wearables" / "google_fit_heartrate.json")


@pytest.fixture
def ambulance_xml(sample_data_dir):
    return str(sample_data_dir / "ambulance" / "ems_run_001.xml")


@pytest.fixture
def bedside_json(sample_data_dir):
    return str(sample_data_dir / "realtime_vitals" / "bedside_stream_001.json")


@pytest.fixture
def ecg_csv(sample_data_dir):
    return str(sample_data_dir / "realtime_vitals" / "bedside_waveform_001.csv")


@pytest.fixture
def dicom_file(sample_data_dir):
    path = str(sample_data_dir / "scans_labs" / "chest_xray_001.dcm")
    if not os.path.exists(path):
        pytest.skip("DICOM sample file not found")
    return path


@pytest.fixture
def pdf_lab(sample_data_dir):
    path = str(sample_data_dir / "scans_labs" / "blood_panel_001.pdf")
    if not os.path.exists(path):
        pytest.skip("PDF lab report sample not found")
    return path


@pytest.fixture
def handwritten_note(sample_data_dir):
    path = str(sample_data_dir / "handwritten" / "clinical_note_001.png")
    if not os.path.exists(path):
        pytest.skip("Handwritten note sample not found")
    return path
