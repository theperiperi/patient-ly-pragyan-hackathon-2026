"""Mock STT client for testing without real API calls."""

from __future__ import annotations

from voice.stt.base import TranscriptionResult

_DEFAULT_TRANSCRIPT = (
    "Patient is Rajesh Kumar, 45 year old male. "
    "Date of birth 15th August 1980. "
    "MRN number MRN-2024-001234. "
    "He is complaining of severe chest pain radiating to left arm since 2 hours. "
    "Blood pressure 140 over 90. Heart rate 88 beats per minute. "
    "SpO2 is 96 percent. Temperature 37.2 degrees. "
    "Respiratory rate 20. "
    "Known case of hypertension and type 2 diabetes. "
    "Currently on Amlodipine 5mg and Metformin 500mg."
)


class MockSTTClient:
    """Returns configurable transcript for testing."""

    def __init__(self, transcript: str | None = None):
        self._transcript = transcript or _DEFAULT_TRANSCRIPT

    def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> TranscriptionResult:
        return TranscriptionResult(
            text=self._transcript,
            language=language or "en",
            confidence=0.95,
            duration_seconds=30.0,
        )
