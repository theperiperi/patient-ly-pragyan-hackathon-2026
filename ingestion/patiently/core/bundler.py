"""FHIR Transaction Bundle creation per patient."""

from __future__ import annotations

import uuid

from fhir.resources.R4B.bundle import Bundle, BundleEntry, BundleEntryRequest

from patiently.core.patient_linker import LinkedPatient


class FHIRBundler:
    """Creates FHIR Transaction Bundles from linked patient data."""

    def create_patient_bundle(self, linked_patient: LinkedPatient) -> Bundle:
        """Create a FHIR transaction Bundle for one patient."""
        entries = []

        # 1. Patient resource first
        patient = linked_patient.fhir_patient
        if patient is None:
            raise ValueError("LinkedPatient has no FHIR Patient resource")

        patient_fullurl = f"urn:uuid:{uuid.uuid4()}"
        entries.append(BundleEntry(
            fullUrl=patient_fullurl,
            resource=patient,
            request=BundleEntryRequest(method="POST", url="Patient"),
        ))

        # 2. All other resources, updating subject/patient references
        for resource in linked_patient.all_resources:
            resource_fullurl = f"urn:uuid:{uuid.uuid4()}"
            self._update_patient_reference(resource, patient_fullurl)
            entries.append(BundleEntry(
                fullUrl=resource_fullurl,
                resource=resource,
                request=BundleEntryRequest(
                    method="POST",
                    url=resource.get_resource_type(),
                ),
            ))

        return Bundle(type="transaction", entry=entries)

    @staticmethod
    def _update_patient_reference(resource, patient_fullurl: str) -> None:
        """Update any subject or patient reference to point to the patient's fullUrl."""
        # Check common reference fields
        if hasattr(resource, 'subject') and resource.subject:
            resource.subject.reference = patient_fullurl
        if hasattr(resource, 'patient') and resource.patient:
            resource.patient.reference = patient_fullurl
