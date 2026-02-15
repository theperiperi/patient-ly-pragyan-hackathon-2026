"""OpenAI Whisper API client for speech-to-text."""

from __future__ import annotations

import io

from voice.stt.base import TranscriptionResult
from voice import config as voice_cfg


class WhisperSTTClient:
    """Transcribes audio using OpenAI Whisper API."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or voice_cfg.WHISPER_API_KEY
        self.model = model or voice_cfg.WHISPER_MODEL

    def transcribe(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> TranscriptionResult:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required: pip install openai")

        client = OpenAI(api_key=self.api_key)

        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = filename

        kwargs: dict = {
            "model": self.model,
            "file": audio_file,
            "response_format": "verbose_json",
        }
        if language:
            kwargs["language"] = language

        response = client.audio.transcriptions.create(**kwargs)

        return TranscriptionResult(
            text=response.text,
            language=getattr(response, "language", language),
            duration_seconds=getattr(response, "duration", None),
        )
