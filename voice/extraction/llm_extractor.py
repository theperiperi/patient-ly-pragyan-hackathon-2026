"""LLM-based structured data extraction from voice transcripts."""

from __future__ import annotations

import json
from typing import Any, Protocol

from voice.extraction.prompts import VOICE_EXTRACTION_SYSTEM_PROMPT, VOICE_EXTRACTION_PROMPT
from voice.extraction.schemas import VoiceExtractionResult
from voice import config as voice_cfg


class LLMExtractor(Protocol):
    """Protocol for LLM extraction clients."""

    def extract(self, transcript: str) -> VoiceExtractionResult: ...


def _strip_code_fences(text: str) -> str:
    """Strip markdown code fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        end = -1 if lines[-1].strip().startswith("```") else len(lines)
        text = "\n".join(lines[1:end])
    return text.strip()


class GeminiExtractor:
    """Extracts structured medical data from transcripts using Google Gemini."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or voice_cfg.GEMINI_API_KEY
        self.model = model or voice_cfg.GEMINI_MODEL

    def extract(self, transcript: str) -> VoiceExtractionResult:
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai required: pip install google-generativeai")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(
            self.model,
            system_instruction=VOICE_EXTRACTION_SYSTEM_PROMPT,
        )

        prompt = VOICE_EXTRACTION_PROMPT.format(transcript=transcript)
        response = model.generate_content(prompt)
        text = _strip_code_fences(response.text)
        raw = json.loads(text)
        return VoiceExtractionResult(**raw)


class OpenAIExtractor:
    """Extracts structured medical data using OpenAI GPT-4o."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or voice_cfg.OPENAI_API_KEY
        self.model = model or voice_cfg.OPENAI_MODEL

    def extract(self, transcript: str) -> VoiceExtractionResult:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai required: pip install openai")

        client = OpenAI(api_key=self.api_key)
        prompt = VOICE_EXTRACTION_PROMPT.format(transcript=transcript)

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": VOICE_EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        raw = json.loads(response.choices[0].message.content)
        return VoiceExtractionResult(**raw)


class MockExtractor:
    """Mock extractor for testing."""

    def __init__(self, result: dict[str, Any] | None = None):
        self._result = result

    def extract(self, transcript: str) -> VoiceExtractionResult:
        if self._result:
            return VoiceExtractionResult(**self._result)

        return VoiceExtractionResult(
            patient_name="Rajesh Kumar",
            given_name="Rajesh",
            family_name="Kumar",
            birth_date="1980-08-15",
            gender="male",
            mrn="MRN-2024-001234",
            chief_complaint="Severe chest pain radiating to left arm, onset 2 hours ago",
            vitals={
                "heart_rate": 88,
                "blood_pressure_systolic": 140,
                "blood_pressure_diastolic": 90,
                "spo2": 96,
                "temperature": 37.2,
                "respiratory_rate": 20,
            },
            diagnoses=[
                {"code": "I10", "description": "Essential hypertension", "clinical_status": "active"},
                {"code": "E11", "description": "Type 2 diabetes mellitus", "clinical_status": "active"},
            ],
            medications=["Amlodipine 5mg", "Metformin 500mg"],
        )
