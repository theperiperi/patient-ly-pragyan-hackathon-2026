"""Voice adapter -- transcribes audio, extracts structured data, produces FHIR resources."""

from __future__ import annotations

from datetime import datetime, timezone

from ingest.core.base_adapter import PatientIdentity, AdapterResult
from ingest.core.fhir_helpers import (
    make_patient,
    make_observation_vital,
    make_observation_bp,
    make_condition,
    make_encounter,
)
from ingest import config as cfg

from voice.stt.base import STTClient, TranscriptionResult
from voice.extraction.llm_extractor import LLMExtractor
from voice.extraction.schemas import VoiceExtractionResult


class VoiceAdapter:
    """Transcribes audio and extracts structured FHIR resources."""

    SOURCE_TYPE = "voice_input"

    def __init__(self, stt_client: STTClient, extractor: LLMExtractor):
        self._stt = stt_client
        self._extractor = extractor

    def process_audio(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language: str | None = None,
    ) -> AdapterResult:
        """Full pipeline: audio -> transcript -> structured extraction -> FHIR resources."""
        transcription = self._stt.transcribe(audio_bytes, filename, language)
        extracted = self._extractor.extract(transcription.text)
        return self._build_adapter_result(extracted, transcription)

    def process_transcript(self, transcript: str) -> AdapterResult:
        """Process a pre-existing text transcript (skip STT step)."""
        extracted = self._extractor.extract(transcript)
        transcription = TranscriptionResult(text=transcript)
        return self._build_adapter_result(extracted, transcription)

    def _build_adapter_result(
        self,
        extracted: VoiceExtractionResult,
        transcription: TranscriptionResult,
    ) -> AdapterResult:
        """Convert extraction result to AdapterResult with FHIR resources."""
        identity = self._build_identity(extracted)
        patient = make_patient(identity)
        patient_ref = f"Patient/{patient.id}"
        resources: list = []
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Encounter
        enc = extracted.encounter
        if enc and enc.encounter_class:
            class_map = {
                "emergency": ("EMER", "emergency"),
                "inpatient": ("IMP", "inpatient"),
                "outpatient": ("AMB", "ambulatory"),
            }
            cls_code, cls_display = class_map.get(
                enc.encounter_class, ("AMB", "ambulatory")
            )
            resources.append(
                make_encounter(
                    patient_ref,
                    cls_code,
                    cls_display,
                    enc.period_start or now_iso,
                    enc.period_end,
                    status=enc.status or "in-progress",
                )
            )

        # Vitals
        v = extracted.vitals
        if v.heart_rate is not None:
            resources.append(
                make_observation_vital(
                    patient_ref, cfg.LOINC_HEART_RATE, v.heart_rate,
                    "beats/minute", cfg.UCUM_BPM, now_iso,
                )
            )

        if v.spo2 is not None:
            resources.append(
                make_observation_vital(
                    patient_ref, cfg.LOINC_SPO2, v.spo2,
                    "%", cfg.UCUM_PERCENT, now_iso,
                )
            )

        if v.blood_pressure_systolic is not None and v.blood_pressure_diastolic is not None:
            resources.append(
                make_observation_bp(
                    patient_ref, v.blood_pressure_systolic,
                    v.blood_pressure_diastolic, now_iso,
                )
            )

        if v.respiratory_rate is not None:
            resources.append(
                make_observation_vital(
                    patient_ref, cfg.LOINC_RESP_RATE, v.respiratory_rate,
                    "breaths/minute", cfg.UCUM_BPM, now_iso,
                )
            )

        if v.temperature is not None:
            resources.append(
                make_observation_vital(
                    patient_ref, cfg.LOINC_BODY_TEMP, v.temperature,
                    "degC", cfg.UCUM_CELSIUS, now_iso,
                )
            )

        if v.body_weight is not None:
            resources.append(
                make_observation_vital(
                    patient_ref, cfg.LOINC_BODY_WEIGHT, v.body_weight,
                    "kg", cfg.UCUM_KG, now_iso,
                )
            )

        if v.body_height is not None:
            resources.append(
                make_observation_vital(
                    patient_ref, cfg.LOINC_BODY_HEIGHT, v.body_height,
                    "cm", cfg.UCUM_CM, now_iso,
                )
            )

        if v.bmi is not None:
            resources.append(
                make_observation_vital(
                    patient_ref, cfg.LOINC_BMI, v.bmi,
                    "kg/m2", cfg.UCUM_KG_M2, now_iso,
                )
            )

        # Conditions / Diagnoses
        for dx in extracted.diagnoses:
            if dx.description:
                system = cfg.ICD10_SYSTEM if dx.code and dx.code[0].isalpha() else cfg.SNOMED_SYSTEM
                resources.append(
                    make_condition(
                        patient_ref,
                        dx.code or "unknown",
                        dx.description,
                        system,
                        clinical_status=dx.clinical_status,
                        onset_date=dx.onset_date,
                    )
                )

        return AdapterResult(
            patient_identity=identity,
            fhir_resources=resources,
            fhir_patient=patient,
            source_type=self.SOURCE_TYPE,
            raw_metadata={
                "transcript": transcription.text,
                "detected_language": transcription.language,
                "confidence": transcription.confidence,
                "duration_seconds": transcription.duration_seconds,
                "chief_complaint": extracted.chief_complaint,
                "medications": extracted.medications,
                "notes": extracted.notes,
            },
        )

    @staticmethod
    def _build_identity(extracted: VoiceExtractionResult) -> PatientIdentity:
        """Build PatientIdentity from extraction result."""
        given = extracted.given_name
        family = extracted.family_name
        full_name = extracted.patient_name

        if full_name and not given and not family:
            parts = full_name.strip().split()
            if len(parts) >= 2:
                given = parts[0]
                family = parts[-1]
            elif parts:
                given = parts[0]

        return PatientIdentity(
            source_id=f"voice_{extracted.mrn or extracted.patient_name or 'unknown'}",
            source_system="voice_input",
            full_name=full_name,
            given_name=given,
            family_name=family,
            birth_date=extracted.birth_date,
            gender=extracted.gender,
            phone=extracted.phone,
            email=extracted.email,
            mrn=extracted.mrn,
            abha_id=extracted.abha_id,
            address_line=extracted.address_line,
            address_city=extracted.address_city,
            address_state=extracted.address_state,
            address_postal_code=extracted.address_postal_code,
        )
