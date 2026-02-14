"""Shared fixtures for voice tests."""

import struct

import pytest

from voice.stt.mock_client import MockSTTClient
from voice.extraction.llm_extractor import MockExtractor
from voice.adapter import VoiceAdapter


@pytest.fixture
def mock_stt():
    return MockSTTClient()


@pytest.fixture
def mock_extractor():
    return MockExtractor()


@pytest.fixture
def voice_adapter(mock_stt, mock_extractor):
    return VoiceAdapter(stt_client=mock_stt, extractor=mock_extractor)


@pytest.fixture
def sample_audio_bytes():
    """Minimal valid WAV header (silence) for testing."""
    sample_rate = 16000
    num_channels = 1
    bits_per_sample = 16
    data_size = 0
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,
        1,
        num_channels,
        sample_rate,
        sample_rate * num_channels * bits_per_sample // 8,
        num_channels * bits_per_sample // 8,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header


@pytest.fixture
def sample_transcript():
    return (
        "Patient is Rajesh Kumar, 45 year old male. "
        "MRN number MRN-2024-001234. "
        "Complaining of severe chest pain radiating to left arm since 2 hours. "
        "Blood pressure 140 over 90. Heart rate 88. "
        "SpO2 96 percent. Temperature 37.2. Respiratory rate 20."
    )
