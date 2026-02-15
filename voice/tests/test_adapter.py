"""Tests for the VoiceAdapter."""

from voice.adapter import VoiceAdapter
from voice.stt.mock_client import MockSTTClient
from voice.extraction.llm_extractor import MockExtractor


class TestVoiceAdapter:

    def setup_method(self):
        self.adapter = VoiceAdapter(
            stt_client=MockSTTClient(),
            extractor=MockExtractor(),
        )

    def test_process_audio_returns_adapter_result(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        assert result is not None
        assert result.source_type == "voice_input"

    def test_patient_identity_extracted(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        ident = result.patient_identity
        assert ident.full_name == "Rajesh Kumar"
        assert ident.given_name == "Rajesh"
        assert ident.family_name == "Kumar"
        assert ident.gender == "male"
        assert ident.mrn == "MRN-2024-001234"
        assert ident.birth_date == "1980-08-15"

    def test_fhir_patient_created(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        assert result.fhir_patient is not None
        assert result.fhir_patient.get_resource_type() == "Patient"

    def test_vitals_observations_created(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        resource_types = [r.get_resource_type() for r in result.fhir_resources]
        obs_count = resource_types.count("Observation")
        # HR, SpO2, BP, RR, temp = 5 observations
        assert obs_count >= 5

    def test_conditions_created(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        resource_types = [r.get_resource_type() for r in result.fhir_resources]
        cond_count = resource_types.count("Condition")
        # Hypertension + T2DM = 2 conditions
        assert cond_count >= 2

    def test_raw_metadata_contains_transcript(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        assert "transcript" in result.raw_metadata
        assert len(result.raw_metadata["transcript"]) > 0

    def test_raw_metadata_contains_medications(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        meds = result.raw_metadata.get("medications", [])
        assert len(meds) == 2
        assert "Amlodipine 5mg" in meds

    def test_raw_metadata_contains_chief_complaint(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        cc = result.raw_metadata.get("chief_complaint")
        assert cc is not None
        assert "chest pain" in cc.lower()

    def test_process_transcript_skips_stt(self):
        result = self.adapter.process_transcript(
            "Patient John Doe, male, BP 120 over 80, heart rate 72."
        )
        assert result is not None
        assert result.source_type == "voice_input"
        # MockExtractor still returns default mock data regardless of input
        assert result.patient_identity.full_name == "Rajesh Kumar"

    def test_condition_uses_icd10_for_alpha_codes(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        conditions = [r for r in result.fhir_resources if r.get_resource_type() == "Condition"]
        # I10 and E11 both start with letters -> ICD-10
        for cond in conditions:
            code_system = cond.code.coding[0].system
            assert code_system == "http://hl7.org/fhir/sid/icd-10"

    def test_bp_observation_has_components(self, sample_audio_bytes):
        result = self.adapter.process_audio(sample_audio_bytes)
        bp_obs = [
            r for r in result.fhir_resources
            if r.get_resource_type() == "Observation" and r.component is not None
        ]
        assert len(bp_obs) == 1
        assert len(bp_obs[0].component) == 2
        # Systolic = 140, Diastolic = 90
        vals = sorted([c.valueQuantity.value for c in bp_obs[0].component])
        assert vals == [90, 140]
