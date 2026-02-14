"""Tests for the FHIR Bundler."""

import pytest
from patiently.core.base_adapter import PatientIdentity
from patiently.core.fhir_helpers import make_patient, make_observation_vital
from patiently.core.patient_linker import LinkedPatient
from patiently.core.bundler import FHIRBundler
from patiently import config as cfg


class TestFHIRBundler:

    def setup_method(self):
        self.bundler = FHIRBundler()

    def _make_linked_patient(self, num_obs=3):
        identity = PatientIdentity(
            source_id="MRN001", source_system="test",
            given_name="Rajesh", family_name="Kumar",
            mrn="MRN001", birth_date="1975-08-15", gender="male",
        )
        patient = make_patient(identity)
        resources = []
        for i in range(num_obs):
            resources.append(make_observation_vital(
                f"Patient/{patient.id}", cfg.LOINC_HEART_RATE, 72.0 + i,
                "beats/minute", cfg.UCUM_BPM, "2026-01-01T00:00:00Z"
            ))
        return LinkedPatient(
            canonical_id="test-123",
            identities=[identity],
            fhir_patient=patient,
            all_resources=resources,
            source_types={"test"},
        )

    def test_bundle_type_is_transaction(self):
        lp = self._make_linked_patient()
        bundle = self.bundler.create_patient_bundle(lp)
        assert bundle.type == "transaction"

    def test_patient_is_first_entry(self):
        lp = self._make_linked_patient()
        bundle = self.bundler.create_patient_bundle(lp)
        first = bundle.entry[0]
        assert first.resource.get_resource_type() == "Patient"
        assert first.request.method == "POST"
        assert first.request.url == "Patient"

    def test_entry_count(self):
        lp = self._make_linked_patient(num_obs=3)
        bundle = self.bundler.create_patient_bundle(lp)
        assert len(bundle.entry) == 4

    def test_all_entries_have_fullurl(self):
        lp = self._make_linked_patient()
        bundle = self.bundler.create_patient_bundle(lp)
        for entry in bundle.entry:
            assert entry.fullUrl is not None
            assert entry.fullUrl.startswith("urn:uuid:")

    def test_subject_references_updated(self):
        lp = self._make_linked_patient()
        bundle = self.bundler.create_patient_bundle(lp)
        patient_url = bundle.entry[0].fullUrl
        for entry in bundle.entry[1:]:
            if hasattr(entry.resource, "subject") and entry.resource.subject:
                assert entry.resource.subject.reference == patient_url

    def test_bundle_serializes_to_json(self):
        lp = self._make_linked_patient()
        bundle = self.bundler.create_patient_bundle(lp)
        json_str = bundle.json()
        assert "Bundle" in json_str
