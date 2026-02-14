"""Tests for the Hospital EHR (HL7 v2) adapter."""

import pytest
from ingest.adapters.ehr_adapter import EHRAdapter


class TestEHRAdapter:

    def setup_method(self):
        self.adapter = EHRAdapter()

    def test_source_type(self):
        assert self.adapter.source_type == "hospital_ehr"

    def test_supports_hl7_file(self, ehr_admission):
        assert self.adapter.supports(ehr_admission) is True

    def test_supports_rejects_json(self, bedside_json):
        assert self.adapter.supports(bedside_json) is False

    def test_supports_rejects_nonexistent(self):
        assert self.adapter.supports("/nonexistent/file.hl7") is False

    def test_supports_raw_hl7_string(self):
        msg = "MSH|^~\\&|HIS|HOSP|OUT|SYS|20260101||ADT^A01|1|P|2.5\rPID|||MRN001||Doe^John||19900101|M"
        assert self.adapter.supports(msg) is True

    def test_parse_admission(self, ehr_admission):
        result = self.adapter.parse(ehr_admission)
        assert result is not None
        assert result.source_type == "hospital_ehr"
        assert result.patient_identity.mrn == "MRN-2024-001234"
        assert result.patient_identity.family_name == "Kumar"
        assert result.patient_identity.given_name == "Rajesh"
        assert result.patient_identity.gender == "male"
        assert result.fhir_patient is not None
        assert len(result.fhir_resources) >= 3
        resource_types = [r.get_resource_type() for r in result.fhir_resources]
        assert "Encounter" in resource_types
        assert "Observation" in resource_types
        assert "Condition" in resource_types

    def test_parse_lab_results(self, ehr_lab):
        result = self.adapter.parse(ehr_lab)
        assert result is not None
        assert result.patient_identity.mrn == "MRN-2024-001234"
        resource_types = [r.get_resource_type() for r in result.fhir_resources]
        assert "Observation" in resource_types
        assert "DiagnosticReport" in resource_types

    def test_fhir_patient_has_name(self, ehr_admission):
        result = self.adapter.parse(ehr_admission)
        patient = result.fhir_patient
        assert patient.name is not None
        assert len(patient.name) > 0
        assert patient.name[0].family == "Kumar"

    def test_observation_has_loinc_coding(self, ehr_admission):
        result = self.adapter.parse(ehr_admission)
        observations = [r for r in result.fhir_resources if r.get_resource_type() == "Observation"]
        assert len(observations) > 0
        obs = observations[0]
        assert obs.code.coding[0].system == "http://loinc.org"
