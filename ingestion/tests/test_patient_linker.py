"""Tests for the Patient Linker."""

import pytest
from ingest.core.base_adapter import PatientIdentity, AdapterResult
from ingest.core.fhir_helpers import make_patient, make_observation_vital
from ingest.core.patient_linker import PatientLinker
from ingest import config as cfg


def _make_result(identity, source_type="test", num_obs=1):
    patient = make_patient(identity)
    resources = []
    for i in range(num_obs):
        resources.append(make_observation_vital(
            f"Patient/{patient.id}", cfg.LOINC_HEART_RATE, 72.0 + i,
            "beats/minute", cfg.UCUM_BPM, "2026-01-01T00:00:00Z"
        ))
    return AdapterResult(
        patient_identity=identity,
        fhir_resources=resources,
        fhir_patient=patient,
        source_type=source_type,
    )


class TestPatientLinker:

    def setup_method(self):
        self.linker = PatientLinker()

    def test_single_source_creates_patient(self):
        identity = PatientIdentity(source_id="1", source_system="test", mrn="MRN001")
        result = _make_result(identity)
        lp = self.linker.ingest(result)
        assert lp is not None
        assert len(self.linker.get_all_patients()) == 1

    def test_mrn_match_links_patients(self):
        id1 = PatientIdentity(source_id="1", source_system="ehr", mrn="MRN001",
                              given_name="Rajesh", family_name="Kumar")
        id2 = PatientIdentity(source_id="2", source_system="wearable", mrn="MRN001",
                              given_name="Rajesh", family_name="Kumar")
        self.linker.ingest(_make_result(id1, "ehr"))
        self.linker.ingest(_make_result(id2, "wearable"))
        patients = self.linker.get_all_patients()
        assert len(patients) == 1
        assert len(patients[0].identities) == 2
        assert patients[0].source_types == {"ehr", "wearable"}

    def test_name_dob_match_links_patients(self):
        id1 = PatientIdentity(source_id="1", source_system="ehr",
                              full_name="Rajesh Kumar", birth_date="1975-08-15")
        id2 = PatientIdentity(source_id="2", source_system="wearable",
                              full_name="Rajesh Kumar", birth_date="1975-08-15")
        self.linker.ingest(_make_result(id1, "ehr"))
        self.linker.ingest(_make_result(id2, "wearable"))
        assert len(self.linker.get_all_patients()) == 1

    def test_different_patients_stay_separate(self):
        id1 = PatientIdentity(source_id="1", source_system="ehr", mrn="MRN001",
                              full_name="Rajesh Kumar", birth_date="1975-08-15")
        id2 = PatientIdentity(source_id="2", source_system="ehr", mrn="MRN002",
                              full_name="Priya Sharma", birth_date="2007-03-22")
        self.linker.ingest(_make_result(id1, "ehr"))
        self.linker.ingest(_make_result(id2, "ehr"))
        assert len(self.linker.get_all_patients()) == 2

    def test_merged_patient_has_most_complete_fields(self):
        id1 = PatientIdentity(source_id="1", source_system="ehr", mrn="MRN001",
                              given_name="Rajesh", family_name="Kumar")
        id2 = PatientIdentity(source_id="2", source_system="wearable", mrn="MRN001",
                              birth_date="1975-08-15", gender="male")
        self.linker.ingest(_make_result(id1, "ehr"))
        lp = self.linker.ingest(_make_result(id2, "wearable"))
        patient = lp.fhir_patient
        assert patient.name[0].family == "Kumar"
        assert patient.gender == "male"
        assert str(patient.birthDate) == "1975-08-15"

    def test_resources_aggregated(self):
        id1 = PatientIdentity(source_id="1", source_system="ehr", mrn="MRN001")
        id2 = PatientIdentity(source_id="2", source_system="wearable", mrn="MRN001")
        self.linker.ingest(_make_result(id1, "ehr", num_obs=3))
        lp = self.linker.ingest(_make_result(id2, "wearable", num_obs=2))
        assert len(lp.all_resources) == 5
