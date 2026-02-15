"""Extract clinical resources from FHIR bundles and generate context hints."""

from datetime import date, datetime
from typing import Optional

from ..config import (
    CARDIAC_CONDITIONS,
    ELDERLY_AGE,
    HIGH_RISK_CONDITIONS,
    IMMUNOCOMPROMISING_CONDITIONS,
    PEDIATRIC_AGE,
    POLYPHARMACY_THRESHOLD,
    RECENT_ED_DAYS,
    RESPIRATORY_CONDITIONS,
)
from ..models import (
    Allergy,
    Condition,
    ContextHints,
    Encounter,
    Medication,
    PatientBasic,
    PatientSnapshot,
    Vital,
)
from .loader import get_loader


class ResourceExtractor:
    """Extract clinical resources from FHIR bundles."""

    def __init__(self):
        self.loader = get_loader()

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse FHIR date string to date object."""
        if not date_str:
            return None
        try:
            # Handle various FHIR date formats
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
            return date.fromisoformat(date_str)
        except Exception:
            return None

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse FHIR datetime string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return None

    def _calculate_age(self, birth_date: date) -> int:
        """Calculate age from birth date."""
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age

    def _is_condition_match(self, display: str, keywords: list[str]) -> bool:
        """Check if condition display text matches any keywords."""
        display_lower = display.lower()
        return any(kw in display_lower for kw in keywords)

    def _get_bundle(self, patient_id: str) -> Optional[dict]:
        """Get bundle by patient_id or ABHA address."""
        # Try ABHA address lookup first if it looks like an ABHA address
        if "@abdm" in patient_id:
            bundle = self.loader.get_bundle_by_abha(patient_id)
            if bundle:
                return bundle
        # Fall back to direct patient ID lookup
        return self.loader.get_bundle(patient_id)

    def _get_actual_patient_id(self, patient_id: str) -> str:
        """Resolve ABHA address to actual patient UUID if needed."""
        if "@abdm" in patient_id:
            resolved = self.loader.abha_to_id.get(patient_id)
            if resolved:
                return resolved
        return patient_id

    def extract_patient_basic(self, patient_id: str) -> Optional[PatientBasic]:
        """Extract basic patient info."""
        bundle = self._get_bundle(patient_id)
        if not bundle:
            return None

        patient = None
        for entry in bundle.get("entry", []):
            res = entry.get("resource", {})
            if res.get("resourceType") == "Patient":
                patient = res
                break

        if not patient:
            return None

        # Extract identifiers
        abha_number = ""
        abha_address = ""
        for identifier in patient.get("identifier", []):
            system = identifier.get("system", "")
            value = identifier.get("value", "")
            if "abha-address" in system.lower():
                abha_address = value
            elif "healthid" in system.lower():
                abha_number = value

        # Extract name
        name = ""
        for n in patient.get("name", []):
            if n.get("text"):
                name = n.get("text")
                break
            given = " ".join(n.get("given", []))
            family = n.get("family", "")
            name = f"{given} {family}".strip()
            break

        # Extract address
        city = ""
        state = ""
        for addr in patient.get("address", []):
            city = addr.get("city", "")
            state = addr.get("state", "")
            break

        # Parse birth date and calculate age
        birth_date_str = patient.get("birthDate", "")
        birth_date = self._parse_date(birth_date_str) or date(1900, 1, 1)
        age = self._calculate_age(birth_date)

        return PatientBasic(
            patient_id=patient_id,
            abha_number=abha_number,
            abha_address=abha_address,
            name=name,
            gender=patient.get("gender", "unknown"),
            date_of_birth=birth_date,
            age=age,
            city=city,
            state=state,
        )

    def extract_conditions(self, patient_id: str) -> list[Condition]:
        """Extract conditions from patient bundle."""
        actual_id = self._get_actual_patient_id(patient_id)
        resources = self.loader.get_resources_by_type(actual_id, "Condition")
        conditions = []

        for res in resources:
            # Extract code and display
            code_obj = res.get("code", {})
            coding = code_obj.get("coding", [{}])[0]
            code = coding.get("code", "")
            display = coding.get("display", "") or code_obj.get("text", "")

            # Extract clinical status
            status_obj = res.get("clinicalStatus", {})
            status_coding = status_obj.get("coding", [{}])[0]
            clinical_status = status_coding.get("code", "unknown")

            # Extract onset date
            onset_str = res.get("onsetDateTime") or res.get("recordedDate")
            onset_date = self._parse_date(onset_str)

            # Determine risk flags
            is_high_risk = self._is_condition_match(display, HIGH_RISK_CONDITIONS)
            is_cardiac = self._is_condition_match(display, CARDIAC_CONDITIONS)
            is_respiratory = self._is_condition_match(display, RESPIRATORY_CONDITIONS)
            is_immunocompromising = self._is_condition_match(display, IMMUNOCOMPROMISING_CONDITIONS)

            conditions.append(Condition(
                code=code,
                display=display,
                clinical_status=clinical_status,
                onset_date=onset_date,
                is_high_risk=is_high_risk,
                is_cardiac=is_cardiac,
                is_respiratory=is_respiratory,
                is_immunocompromising=is_immunocompromising,
            ))

        return conditions

    def extract_medications(self, patient_id: str) -> list[Medication]:
        """Extract medications from patient bundle."""
        actual_id = self._get_actual_patient_id(patient_id)
        resources = self.loader.get_resources_by_type(actual_id, "MedicationRequest")
        medications = []

        for res in resources:
            # Extract medication code
            med_obj = res.get("medicationCodeableConcept", {})
            coding = med_obj.get("coding", [{}])[0]
            code = coding.get("code", "")
            display = coding.get("display", "") or med_obj.get("text", "")

            # Extract status
            status = res.get("status", "unknown")

            # Extract dosage
            dosage = ""
            dosage_instructions = res.get("dosageInstruction", [])
            if dosage_instructions:
                di = dosage_instructions[0]
                dosage_text = di.get("text", "")
                if dosage_text:
                    dosage = dosage_text
                else:
                    # Try to construct from dose and frequency
                    dose_qty = di.get("doseAndRate", [{}])[0].get("doseQuantity", {})
                    if dose_qty:
                        dosage = f"{dose_qty.get('value', '')} {dose_qty.get('unit', '')}".strip()

            # Extract start date
            start_str = res.get("authoredOn")
            start_date = self._parse_date(start_str)

            medications.append(Medication(
                code=code,
                display=display,
                status=status,
                dosage=dosage or None,
                start_date=start_date,
            ))

        return medications

    def extract_allergies(self, patient_id: str) -> list[Allergy]:
        """Extract allergies from patient bundle."""
        actual_id = self._get_actual_patient_id(patient_id)
        resources = self.loader.get_resources_by_type(actual_id, "AllergyIntolerance")
        allergies = []

        for res in resources:
            # Extract code
            code_obj = res.get("code", {})
            coding = code_obj.get("coding", [{}])[0]
            code = coding.get("code", "")
            display = coding.get("display", "") or code_obj.get("text", "")

            # Extract category
            categories = res.get("category", [])
            category = categories[0] if categories else None

            # Extract criticality
            criticality = res.get("criticality")

            # Extract reaction type
            reaction_type = None
            reactions = res.get("reaction", [])
            if reactions:
                manifestations = reactions[0].get("manifestation", [])
                if manifestations:
                    manifest_coding = manifestations[0].get("coding", [{}])[0]
                    reaction_type = manifest_coding.get("display")

            allergies.append(Allergy(
                code=code,
                display=display,
                category=category,
                criticality=criticality,
                reaction_type=reaction_type,
            ))

        return allergies

    def extract_vitals(self, patient_id: str, limit: int = 10) -> list[Vital]:
        """Extract recent vital signs from patient bundle."""
        actual_id = self._get_actual_patient_id(patient_id)
        resources = self.loader.get_resources_by_type(actual_id, "Observation")
        vitals = []

        # Vital sign codes to look for
        vital_codes = {
            "8310-5": "Body temperature",
            "8867-4": "Heart rate",
            "9279-1": "Respiratory rate",
            "8480-6": "Systolic blood pressure",
            "8462-4": "Diastolic blood pressure",
            "2708-6": "Oxygen saturation",
            "29463-7": "Body weight",
            "8302-2": "Body height",
            "39156-5": "Body mass index",
        }

        for res in resources:
            code_obj = res.get("code", {})
            coding = code_obj.get("coding", [{}])[0]
            code = coding.get("code", "")

            # Only include vital signs
            if code not in vital_codes:
                # Also check for vital sign category
                categories = res.get("category", [])
                is_vital = False
                for cat in categories:
                    for cat_coding in cat.get("coding", []):
                        if cat_coding.get("code") == "vital-signs":
                            is_vital = True
                            break
                if not is_vital:
                    continue

            display = coding.get("display", "") or vital_codes.get(code, "Observation")

            # Extract value
            value = ""
            unit = ""
            if "valueQuantity" in res:
                vq = res["valueQuantity"]
                value = str(vq.get("value", ""))
                unit = vq.get("unit", "")
            elif "valueCodeableConcept" in res:
                vc = res["valueCodeableConcept"]
                value = vc.get("text", "") or vc.get("coding", [{}])[0].get("display", "")
            elif "valueString" in res:
                value = res["valueString"]

            # Extract date
            effective_str = res.get("effectiveDateTime") or res.get("issued")
            recorded_date = self._parse_datetime(effective_str)

            vitals.append(Vital(
                code=code,
                display=display,
                value=value,
                unit=unit or None,
                recorded_date=recorded_date,
            ))

        # Sort by date (most recent first) and limit
        vitals.sort(key=lambda v: v.recorded_date or datetime.min, reverse=True)
        return vitals[:limit]

    def extract_encounters(self, patient_id: str, days_back: int = 365) -> list[Encounter]:
        """Extract encounters from patient bundle."""
        actual_id = self._get_actual_patient_id(patient_id)
        resources = self.loader.get_resources_by_type(actual_id, "Encounter")
        encounters = []
        today = date.today()

        for res in resources:
            encounter_id = res.get("id", "")
            status = res.get("status", "unknown")

            # Extract type
            types = res.get("type", [])
            encounter_type = ""
            if types:
                coding = types[0].get("coding", [{}])[0]
                encounter_type = coding.get("display", "") or types[0].get("text", "")

            # Extract class
            class_obj = res.get("class", {})
            encounter_class = class_obj.get("code", "")

            # Check if emergency
            is_emergency = encounter_class in ["EMER", "emergency"]

            # Extract start date
            period = res.get("period", {})
            start_str = period.get("start")
            start_date = self._parse_date(start_str)

            # Calculate days ago
            days_ago = 0
            if start_date:
                days_ago = (today - start_date).days

            # Filter by days_back
            if days_back > 0 and days_ago > days_back:
                continue

            # Extract reason
            reason = ""
            reasons = res.get("reasonCode", [])
            if reasons:
                reason_coding = reasons[0].get("coding", [{}])[0]
                reason = reason_coding.get("display", "") or reasons[0].get("text", "")

            encounters.append(Encounter(
                encounter_id=encounter_id,
                encounter_type=encounter_type,
                encounter_class=encounter_class,
                status=status,
                start_date=start_date,
                reason=reason or None,
                is_emergency=is_emergency,
                days_ago=days_ago,
            ))

        # Sort by date (most recent first)
        encounters.sort(key=lambda e: e.start_date or date.min, reverse=True)
        return encounters

    def generate_hints(
        self,
        age: int,
        conditions: list[Condition],
        medications: list[Medication],
        allergies: list[Allergy],
        encounters: list[Encounter],
    ) -> ContextHints:
        """Generate context hints from clinical data."""
        active_conditions = [c for c in conditions if c.clinical_status == "active"]
        active_medications = [m for m in medications if m.status == "active"]

        # Check for recent ED visits
        recent_ed = any(
            e.is_emergency and e.days_ago <= RECENT_ED_DAYS
            for e in encounters
        )

        # Collect high-risk condition names
        high_risk = [c.display for c in active_conditions if c.is_high_risk]

        return ContextHints(
            elderly=age >= ELDERLY_AGE,
            pediatric=age < PEDIATRIC_AGE,
            cardiac_history=any(c.is_cardiac for c in conditions),
            respiratory_history=any(c.is_respiratory for c in conditions),
            diabetic=any("diabetes" in c.display.lower() for c in active_conditions),
            polypharmacy=len(active_medications) >= POLYPHARMACY_THRESHOLD,
            recent_ed_visit=recent_ed,
            high_risk_conditions=high_risk,
            allergy_count=len(allergies),
            immunocompromised=any(c.is_immunocompromising for c in conditions),
            active_condition_count=len(active_conditions),
            active_medication_count=len(active_medications),
        )

    def get_patient_snapshot(self, patient_id: str) -> Optional[PatientSnapshot]:
        """Get comprehensive patient snapshot with context hints."""
        basic = self.extract_patient_basic(patient_id)
        if not basic:
            return None

        conditions = self.extract_conditions(patient_id)
        medications = self.extract_medications(patient_id)
        allergies = self.extract_allergies(patient_id)
        vitals = self.extract_vitals(patient_id)
        encounters = self.extract_encounters(patient_id, days_back=365)

        # Generate context hints
        hints = self.generate_hints(
            age=basic.age,
            conditions=conditions,
            medications=medications,
            allergies=allergies,
            encounters=encounters,
        )

        # Get full patient resource for phone/address
        bundle = self._get_bundle(patient_id)
        phone = None
        address_line = None
        if bundle:
            for entry in bundle.get("entry", []):
                res = entry.get("resource", {})
                if res.get("resourceType") == "Patient":
                    # Extract phone
                    for telecom in res.get("telecom", []):
                        if telecom.get("system") == "phone":
                            phone = telecom.get("value")
                            break
                    # Extract address line
                    for addr in res.get("address", []):
                        lines = addr.get("line", [])
                        if lines:
                            address_line = lines[0]
                        break
                    break

        return PatientSnapshot(
            patient_id=patient_id,
            abha_number=basic.abha_number,
            abha_address=basic.abha_address,
            name=basic.name,
            gender=basic.gender,
            date_of_birth=basic.date_of_birth,
            age=basic.age,
            phone=phone,
            address=address_line,
            city=basic.city,
            state=basic.state,
            conditions=conditions,
            medications=medications,
            allergies=allergies,
            recent_vitals=vitals,
            recent_encounters=encounters[:10],  # Limit recent encounters
            hints=hints,
        )


# Global extractor instance
_extractor: Optional[ResourceExtractor] = None


def get_extractor() -> ResourceExtractor:
    """Get global extractor instance."""
    global _extractor
    if _extractor is None:
        _extractor = ResourceExtractor()
    return _extractor
