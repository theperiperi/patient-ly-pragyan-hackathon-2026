"""Tests for the Ambulance/EMS adapter."""

import pytest
from ingest.adapters.ambulance_adapter import AmbulanceAdapter


class TestAmbulanceAdapter:

    def setup_method(self):
        self.adapter = AmbulanceAdapter()

    def test_source_type(self):
        assert self.adapter.source_type == "ambulance_ems"

    def test_supports_nemsis_xml(self, ambulance_xml):
        assert self.adapter.supports(ambulance_xml) is True

    def test_supports_rejects_json(self, bedside_json):
        assert self.adapter.supports(bedside_json) is False

    def test_parse_nemsis(self, ambulance_xml):
        result = self.adapter.parse(ambulance_xml)
        assert result is not None
        assert result.source_type == "ambulance_ems"
        assert result.patient_identity.family_name
        assert result.patient_identity.given_name
        resource_types = [r.get_resource_type() for r in result.fhir_resources]
        assert "Encounter" in resource_types
        assert "Observation" in resource_types
        assert len(result.fhir_resources) >= 10
