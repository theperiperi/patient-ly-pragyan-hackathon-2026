"""FastAPI server for voice-based symptom input."""

from __future__ import annotations

import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ingest.core.bundler import FHIRBundler
from ingest.core.patient_linker import PatientLinker

from voice.stt.whisper_client import WhisperSTTClient
from voice.stt.mock_client import MockSTTClient
from voice.extraction.llm_extractor import GeminiExtractor, MockExtractor
from voice.adapter import VoiceAdapter
from voice import config as voice_cfg

app = FastAPI(
    title="Patient.ly Voice Ingestion API",
    description="Voice-based symptom input with FHIR R4 output",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_adapter(use_mock: bool = False) -> VoiceAdapter:
    """Factory to create VoiceAdapter with appropriate clients."""
    if use_mock:
        return VoiceAdapter(stt_client=MockSTTClient(), extractor=MockExtractor())
    return VoiceAdapter(stt_client=WhisperSTTClient(), extractor=GeminiExtractor())


def _serialize_result(result):
    """Serialize an AdapterResult to a JSON-safe dict."""
    resources = [json.loads(r.json()) for r in result.fhir_resources]
    patient_dict = json.loads(result.fhir_patient.json()) if result.fhir_patient else None
    return {
        "source_type": result.source_type,
        "transcript": result.raw_metadata.get("transcript"),
        "detected_language": result.raw_metadata.get("detected_language"),
        "patient_identity": {
            "full_name": result.patient_identity.full_name,
            "birth_date": result.patient_identity.birth_date,
            "gender": result.patient_identity.gender,
            "mrn": result.patient_identity.mrn,
            "abha_id": result.patient_identity.abha_id,
        },
        "chief_complaint": result.raw_metadata.get("chief_complaint"),
        "medications": result.raw_metadata.get("medications", []),
        "patient_resource": patient_dict,
        "resources_count": len(resources),
        "resources": resources,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "voice-ingestion"}


@app.post("/voice/ingest")
async def ingest_voice(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
    use_mock: bool = Form(default=False),
):
    """Ingest an audio file, transcribe, extract structured data, return FHIR resources.

    Parameters:
    - file: Audio file (wav, mp3, m4a, ogg, flac, webm)
    - language: Optional language hint (e.g., "en", "hi", "ta")
    - use_mock: If True, use mock STT and extractor (for testing)
    """
    filename = file.filename or "audio.wav"
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in voice_cfg.SUPPORTED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format '{ext}'. Supported: {sorted(voice_cfg.SUPPORTED_AUDIO_EXTENSIONS)}",
        )

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    adapter = _get_adapter(use_mock=use_mock)

    try:
        result = adapter.process_audio(audio_bytes, filename, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    return JSONResponse(content=_serialize_result(result))


@app.post("/voice/ingest/transcript")
async def ingest_transcript(
    transcript: str = Form(...),
    use_mock: bool = Form(default=False),
):
    """Ingest a text transcript directly (skip STT), extract structured data, return FHIR resources.

    Useful for testing extraction without audio, or pre-transcribed text.
    """
    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Empty transcript")

    adapter = _get_adapter(use_mock=use_mock)

    try:
        result = adapter.process_transcript(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    return JSONResponse(content=_serialize_result(result))


@app.post("/voice/ingest/bundle")
async def ingest_voice_bundle(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
    use_mock: bool = Form(default=False),
):
    """Ingest audio and return a complete FHIR Transaction Bundle.

    Produces output compatible with the main ingestion pipeline's bundle format.
    """
    filename = file.filename or "audio.wav"
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in voice_cfg.SUPPORTED_AUDIO_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format '{ext}'.")

    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    adapter = _get_adapter(use_mock=use_mock)

    try:
        result = adapter.process_audio(audio_bytes, filename, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    # Run through linker + bundler
    linker = PatientLinker()
    linker.ingest(result)
    linked = linker.get_all_patients()

    bundler = FHIRBundler()
    bundles = [bundler.create_patient_bundle(lp) for lp in linked]

    serialized = []
    for bundle in bundles:
        bundle_dict = json.loads(bundle.json())
        serialized.append({
            "entry_count": len(bundle.entry),
            "bundle": bundle_dict,
        })

    return JSONResponse(content={
        "source_type": result.source_type,
        "transcript": result.raw_metadata.get("transcript"),
        "bundles": serialized,
    })
