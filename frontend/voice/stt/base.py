"""Base protocol for speech-to-text clients."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class TranscriptionResult:
    """Result from speech-to-text transcription."""

    text: str
    language: str | None = None
    confidence: float | None = None
    duration_seconds: float | None = None


class STTClient(Protocol):
    """Protocol for speech-to-text clients."""

    def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> TranscriptionResult: ...
