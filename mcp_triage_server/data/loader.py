"""FHIR bundle loading and indexing."""

import json
from pathlib import Path
from typing import Optional

from ..config import FHIR_BUNDLES_DIR, PATIENTS_INDEX_FILE


class FHIRDataLoader:
    """Load and index FHIR bundles from seed data."""

    def __init__(self, bundles_dir: Path = FHIR_BUNDLES_DIR, index_file: Path = PATIENTS_INDEX_FILE):
        self.bundles_dir = bundles_dir
        self.index_file = index_file
        self.bundles: dict[str, dict] = {}  # patient_id -> bundle
        self.patient_index: dict[str, dict] = {}  # abha_address -> patient info
        self.abha_to_id: dict[str, str] = {}  # abha_address -> patient_id
        self._loaded = False

    def load(self) -> None:
        """Load all FHIR bundles and build index."""
        if self._loaded:
            return

        # Load patient index for quick lookups
        if self.index_file.exists():
            with open(self.index_file) as f:
                patients = json.load(f)
                for p in patients:
                    abha_addr = p.get("abhaAddress", "")
                    self.patient_index[abha_addr] = p

        # Load all FHIR bundles
        for bundle_file in self.bundles_dir.glob("*.json"):
            try:
                with open(bundle_file) as f:
                    bundle = json.load(f)

                # Extract patient ID and ABHA address
                patient_resource = self._find_patient_resource(bundle)
                if patient_resource:
                    patient_id = patient_resource.get("id", "")
                    abha_addr = self._extract_abha_address(patient_resource)

                    if patient_id:
                        self.bundles[patient_id] = bundle
                    if abha_addr and patient_id:
                        self.abha_to_id[abha_addr] = patient_id

            except Exception as e:
                print(f"Error loading {bundle_file}: {e}")

        self._loaded = True
        print(f"Loaded {len(self.bundles)} FHIR bundles")

    def _find_patient_resource(self, bundle: dict) -> Optional[dict]:
        """Find Patient resource in bundle."""
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") == "Patient":
                return resource
        return None

    def _extract_abha_address(self, patient: dict) -> Optional[str]:
        """Extract ABHA address from patient identifiers."""
        for identifier in patient.get("identifier", []):
            system = identifier.get("system", "")
            if "abha-address" in system.lower():
                return identifier.get("value")
        return None

    def get_bundle(self, patient_id: str) -> Optional[dict]:
        """Get FHIR bundle by patient ID."""
        self.load()
        return self.bundles.get(patient_id)

    def get_bundle_by_abha(self, abha_address: str) -> Optional[dict]:
        """Get FHIR bundle by ABHA address."""
        self.load()
        patient_id = self.abha_to_id.get(abha_address)
        if patient_id:
            return self.bundles.get(patient_id)
        return None

    def get_all_patient_ids(self) -> list[str]:
        """Get all patient IDs."""
        self.load()
        return list(self.bundles.keys())

    def get_resources_by_type(self, patient_id: str, resource_type: str) -> list[dict]:
        """Get all resources of a specific type from a patient bundle."""
        bundle = self.get_bundle(patient_id)
        if not bundle:
            return []

        resources = []
        for entry in bundle.get("entry", []):
            resource = entry.get("resource", {})
            if resource.get("resourceType") == resource_type:
                resources.append(resource)
        return resources

    def search_patients(self, query: str) -> list[dict]:
        """Search patients by name, ABHA, or condition."""
        self.load()
        query_lower = query.lower()
        results = []

        for abha_addr, patient_info in self.patient_index.items():
            # Search by name
            name = patient_info.get("name", "").lower()
            if query_lower in name:
                results.append(patient_info)
                continue

            # Search by ABHA address
            if query_lower in abha_addr.lower():
                results.append(patient_info)
                continue

            # Search by patient reference (ABHA number)
            patient_ref = patient_info.get("patientReference", "").lower()
            if query_lower in patient_ref:
                results.append(patient_info)
                continue

        return results

    def get_patient_info(self, patient_id: str) -> Optional[dict]:
        """Get patient info from index by patient ID."""
        self.load()
        # Find by patient ID
        for abha_addr, info in self.patient_index.items():
            if self.abha_to_id.get(abha_addr) == patient_id:
                return info
        return None

    def get_patient_info_by_abha(self, abha_address: str) -> Optional[dict]:
        """Get patient info from index by ABHA address."""
        self.load()
        return self.patient_index.get(abha_address)


# Global loader instance
_loader: Optional[FHIRDataLoader] = None


def get_loader() -> FHIRDataLoader:
    """Get global loader instance."""
    global _loader
    if _loader is None:
        _loader = FHIRDataLoader()
        _loader.load()
    return _loader
