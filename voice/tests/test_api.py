"""Tests for the voice API endpoints."""

import struct

import pytest
from fastapi.testclient import TestClient

from voice.api.server import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def wav_bytes():
    """Minimal valid WAV file bytes."""
    sample_rate = 16000
    data_size = 0
    return struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF", 36 + data_size, b"WAVE",
        b"fmt ", 16, 1, 1, sample_rate,
        sample_rate * 2, 2, 16,
        b"data", data_size,
    )


class TestHealthCheck:

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


class TestVoiceIngest:

    def test_ingest_mock(self, client, wav_bytes):
        resp = client.post(
            "/voice/ingest",
            files={"file": ("test.wav", wav_bytes, "audio/wav")},
            data={"use_mock": "true"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["source_type"] == "voice_input"
        assert body["patient_identity"]["full_name"] == "Rajesh Kumar"
        assert body["resources_count"] >= 7  # 5 vitals + 2 conditions
        assert body["chief_complaint"] is not None
        assert len(body["medications"]) == 2

    def test_ingest_unsupported_format(self, client):
        resp = client.post(
            "/voice/ingest",
            files={"file": ("test.pdf", b"fake", "application/pdf")},
            data={"use_mock": "true"},
        )
        assert resp.status_code == 400
        assert "Unsupported" in resp.json()["detail"]

    def test_ingest_empty_file(self, client):
        resp = client.post(
            "/voice/ingest",
            files={"file": ("test.wav", b"", "audio/wav")},
            data={"use_mock": "true"},
        )
        assert resp.status_code == 400
        assert "Empty" in resp.json()["detail"]


class TestTranscriptIngest:

    def test_ingest_transcript_mock(self, client):
        resp = client.post(
            "/voice/ingest/transcript",
            data={
                "transcript": "Patient John Doe, male, BP 120/80",
                "use_mock": "true",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["source_type"] == "voice_input"
        assert body["resources_count"] >= 1

    def test_ingest_transcript_empty(self, client):
        resp = client.post(
            "/voice/ingest/transcript",
            data={"transcript": "  ", "use_mock": "true"},
        )
        assert resp.status_code == 400


class TestBundleIngest:

    def test_ingest_bundle_mock(self, client, wav_bytes):
        resp = client.post(
            "/voice/ingest/bundle",
            files={"file": ("test.wav", wav_bytes, "audio/wav")},
            data={"use_mock": "true"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["source_type"] == "voice_input"
        assert len(body["bundles"]) >= 1
        bundle = body["bundles"][0]
        assert bundle["entry_count"] >= 1
        assert bundle["bundle"]["resourceType"] == "Bundle"
        assert bundle["bundle"]["type"] == "transaction"
