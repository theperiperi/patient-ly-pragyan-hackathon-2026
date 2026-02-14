"""Tests for the Handwritten Notes adapter."""

import pytest
from ingest.adapters.handwritten_adapter import HandwrittenAdapter
from ingest.api.vlm_client import MockVLMClient


class TestHandwrittenAdapter:

    def setup_method(self):
        self.adapter = HandwrittenAdapter(vlm_client=MockVLMClient())

    def test_source_type(self):
        assert self.adapter.source_type == "handwritten_notes"

    def test_supports_png(self, handwritten_note):
        assert self.adapter.supports(handwritten_note) is True

    def test_supports_rejects_json(self, bedside_json):
        assert self.adapter.supports(bedside_json) is False

    def test_parse_note(self, handwritten_note):
        result = self.adapter.parse(handwritten_note)
        assert result is not None
        assert result.source_type == "handwritten_notes"
        assert result.patient_identity.full_name == "Rajesh Kumar"
        resource_types = [r.get_resource_type() for r in result.fhir_resources]
        assert "DocumentReference" in resource_types
        assert "Condition" in resource_types
        assert "Observation" in resource_types
        # 1 DocRef + 2 conditions + 5 vitals (HR, SpO2, BP, RR, temp)
        assert len(result.fhir_resources) >= 7
