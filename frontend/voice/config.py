"""Configuration for the voice ingestion module."""

import os
from pathlib import Path

# Load .env from project root
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

# --- STT Configuration ---
WHISPER_API_KEY = os.environ.get("OPENAI_API_KEY", "")
WHISPER_MODEL = "whisper-1"

# --- LLM Extraction Configuration ---
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GEMINI_MODEL = "gemini-3-flash-preview"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o"

# --- Supported Audio Formats ---
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".webm"}

# --- Defaults ---
DEFAULT_STT_PROVIDER = "whisper"  # "whisper" | "mock"
DEFAULT_LLM_PROVIDER = "gemini"   # "gemini" | "openai"
