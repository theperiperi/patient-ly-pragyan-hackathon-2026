"""Tests for the Real-Time Vitals adapter."""

import pytest
from ingest.adapters.realtime_vitals_adapter import RealtimeVitalsAdapter


class TestRealtimeVitalsAdapter:

    def setup_method(self):
        self.adapter = RealtimeVitalsAdapter()

    def test_source_type(self):
        assert self.adapter.source_type == "realtime_vitals"

    def test_supports_json(self, bedside_json):
        assert self.adapter.supports(bedside_json) is True

    def test_supports_csv(self, ecg_csv):
        assert self.adapter.supports(ecg_csv) is True

    def test_supports_rejects_hl7(self, ehr_admission):
        assert self.adapter.supports(ehr_admission) is False

    def test_parse_numeric(self, bedside_json):
        result = self.adapter.parse(bedside_json)
        assert result is not None
        assert result.source_type == "realtime_vitals"
        assert result.patient_identity.source_id == "MRN-2024-001234"
        # 6 readings x 6 vitals each = 36 observations
        assert len(result.fhir_resources) >= 30

    def test_parse_waveform(self, ecg_csv):
        result = self.adapter.parse(ecg_csv)
        assert result is not None
        assert len(result.fhir_resources) == 1
        obs = result.fhir_resources[0]
        assert obs.get_resource_type() == "Observation"
        assert obs.valueSampledData is not None
