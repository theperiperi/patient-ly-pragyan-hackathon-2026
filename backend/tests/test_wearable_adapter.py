"""Tests for the Wearable adapter (Apple Health + Google Fit)."""

import pytest
from patiently.adapters.wearable_adapter import WearableAdapter


class TestWearableAdapter:

    def setup_method(self):
        self.adapter = WearableAdapter()

    def test_source_type(self):
        assert self.adapter.source_type == "wearable"

    def test_supports_apple_health(self, apple_health):
        assert self.adapter.supports(apple_health) is True

    def test_supports_google_fit(self, google_fit):
        assert self.adapter.supports(google_fit) is True

    def test_supports_rejects_hl7(self, ehr_admission):
        assert self.adapter.supports(ehr_admission) is False

    def test_parse_apple_health(self, apple_health):
        result = self.adapter.parse(apple_health)
        assert result is not None
        assert result.source_type == "wearable"
        assert result.patient_identity.full_name == "Rajesh Kumar"
        assert result.patient_identity.birth_date == "1975-08-15"
        assert result.patient_identity.gender == "male"
        assert result.patient_identity.mrn == "MRN-2024-001234"
        assert len(result.fhir_resources) >= 5
        for r in result.fhir_resources:
            assert r.get_resource_type() == "Observation"

    def test_parse_google_fit(self, google_fit):
        result = self.adapter.parse(google_fit)
        assert result is not None
        assert result.patient_identity.full_name == "Priya Sharma"
        assert result.patient_identity.gender == "female"
        assert len(result.fhir_resources) >= 3
