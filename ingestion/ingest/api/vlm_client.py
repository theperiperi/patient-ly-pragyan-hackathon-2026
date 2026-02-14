"""Vision-Language Model client for extracting structured data from clinical images."""

from __future__ import annotations

import base64
import json
import os
from typing import Any, Protocol


VLM_EXTRACTION_PROMPT = """Analyze this clinical/medical image and extract structured data as JSON.

Return a JSON object with the following fields (use null for fields you cannot determine):
{
    "patient_name": "Full name",
    "age": "Age as string (e.g. '50y')",
    "gender": "male/female/other",
    "chief_complaint": "Primary reason for visit",
    "vitals": {
        "heart_rate": null,
        "blood_pressure_systolic": null,
        "blood_pressure_diastolic": null,
        "spo2": null,
        "temperature": null,
        "respiratory_rate": null
    },
    "diagnoses": [
        {"code": "ICD-10 code if identifiable", "description": "Diagnosis description"}
    ],
    "medications": ["medication names"],
    "notes": "Any additional clinical notes or observations"
}

Return ONLY valid JSON, no markdown or explanation."""


class VLMClient(Protocol):
    """Protocol for vision-language model clients."""

    def extract_from_image(self, image_bytes: bytes, prompt: str = VLM_EXTRACTION_PROMPT) -> dict[str, Any]:
        """Send an image to a VLM and return structured extraction."""
        ...


class MockVLMClient:
    """Mock VLM client that reads sidecar .meta.json if available, else returns defaults."""

    def __init__(self, image_path: str | None = None):
        self._image_path = image_path

    def extract_from_image(self, image_bytes: bytes, prompt: str = VLM_EXTRACTION_PROMPT) -> dict[str, Any]:
        # Try to load sidecar metadata written by the handwritten simulator
        if self._image_path:
            from pathlib import Path
            sidecar = Path(self._image_path).with_suffix(".meta.json")
            if sidecar.exists():
                return json.loads(sidecar.read_text())

        return {
            "patient_name": "Unknown",
            "age": "50y",
            "gender": "male",
            "chief_complaint": "Chest pain radiating to left arm, onset 2 hours ago",
            "vitals": {
                "heart_rate": 102,
                "blood_pressure_systolic": 158,
                "blood_pressure_diastolic": 94,
                "spo2": 95,
                "temperature": 37.2,
                "respiratory_rate": 22,
            },
            "diagnoses": [
                {"code": "I21.9", "description": "Acute myocardial infarction, unspecified"},
                {"code": "I10", "description": "Essential hypertension"},
            ],
            "medications": ["Aspirin 325mg stat", "Nitroglycerin 0.4mg SL", "Heparin 5000 IU IV"],
            "notes": "ECG shows ST elevation in leads II, III, aVF. Patient diaphoretic, anxious.",
        }


class GeminiVLMClient:
    """Google Gemini 2.0 Flash VLM client (free tier: 100 req/day)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")

    def extract_from_image(self, image_bytes: bytes, prompt: str = VLM_EXTRACTION_PROMPT) -> dict[str, Any]:
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai package required. Install: pip install google-generativeai")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        import PIL.Image
        import io
        image = PIL.Image.open(io.BytesIO(image_bytes))

        response = model.generate_content([prompt, image])
        text = response.text.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        return json.loads(text)


class TogetherVLMClient:
    """Together AI Llama 3.2 Vision 11B client (free tier fallback)."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY", "")

    def extract_from_image(self, image_bytes: bytes, prompt: str = VLM_EXTRACTION_PROMPT) -> dict[str, Any]:
        try:
            from together import Together
        except ImportError:
            raise ImportError("together package required. Install: pip install together")

        client = Together(api_key=self.api_key)
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}},
                ],
            }],
            max_tokens=2048,
        )

        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        return json.loads(text)
