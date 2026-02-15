"""Patient snapshot tool with context hints."""

from typing import Optional

from ..data.extractor import get_extractor
from ..data.loader import get_loader


def _resolve_patient_id(patient_id: str) -> Optional[str]:
    """Resolve patient ID from ID or ABHA address."""
    loader = get_loader()

    # Check if it's already a valid patient ID
    if loader.get_bundle(patient_id):
        return patient_id

    # Try to resolve from ABHA address
    resolved = loader.abha_to_id.get(patient_id)
    if resolved:
        return resolved

    # Try partial match on ABHA address
    for abha_addr, pid in loader.abha_to_id.items():
        if patient_id.lower() in abha_addr.lower():
            return pid

    return None


def get_patient_snapshot(patient_id: str) -> dict:
    """
    Get comprehensive patient snapshot with context hints for triage.

    This tool returns all clinically relevant information about a patient
    along with context hints that surface important indicators for the
    LLM agent to consider when making triage decisions.

    Args:
        patient_id: Patient ID or ABHA address

    Returns:
        Dictionary with:
        - demographics: Patient demographics (name, age, gender, address)
        - conditions: Active and resolved medical conditions
        - medications: Current and past medications
        - allergies: Documented allergies
        - recent_vitals: Recent vital sign observations
        - recent_encounters: Recent healthcare visits
        - hints: Context hints for clinical decision support
            - elderly: True if patient is 65+
            - pediatric: True if patient is under 18
            - cardiac_history: True if cardiac conditions present
            - respiratory_history: True if respiratory conditions present
            - diabetic: True if diabetic condition present
            - polypharmacy: True if 5+ active medications
            - recent_ed_visit: True if ED visit in last 30 days
            - high_risk_conditions: List of flagged high-risk conditions
            - allergy_count: Number of documented allergies
            - immunocompromised: True if immunocompromising conditions
    """
    resolved_id = _resolve_patient_id(patient_id)
    if not resolved_id:
        return {"error": f"Patient not found: {patient_id}"}

    extractor = get_extractor()
    snapshot = extractor.get_patient_snapshot(resolved_id)

    if not snapshot:
        return {"error": f"Could not load patient data: {patient_id}"}

    # Convert conditions
    conditions = []
    for c in snapshot.conditions:
        conditions.append({
            "code": c.code,
            "display": c.display,
            "clinical_status": c.clinical_status,
            "onset_date": c.onset_date.isoformat() if c.onset_date else None,
            "flags": {
                "is_high_risk": c.is_high_risk,
                "is_cardiac": c.is_cardiac,
                "is_respiratory": c.is_respiratory,
                "is_immunocompromising": c.is_immunocompromising,
            },
        })

    # Convert medications
    medications = []
    for m in snapshot.medications:
        medications.append({
            "code": m.code,
            "display": m.display,
            "status": m.status,
            "dosage": m.dosage,
            "start_date": m.start_date.isoformat() if m.start_date else None,
        })

    # Convert allergies
    allergies = []
    for a in snapshot.allergies:
        allergies.append({
            "code": a.code,
            "display": a.display,
            "category": a.category,
            "criticality": a.criticality,
            "reaction_type": a.reaction_type,
        })

    # Convert vitals
    vitals = []
    for v in snapshot.recent_vitals:
        vitals.append({
            "code": v.code,
            "display": v.display,
            "value": v.value,
            "unit": v.unit,
            "recorded_date": v.recorded_date.isoformat() if v.recorded_date else None,
        })

    # Convert encounters
    encounters = []
    for e in snapshot.recent_encounters:
        encounters.append({
            "encounter_id": e.encounter_id,
            "encounter_type": e.encounter_type,
            "encounter_class": e.encounter_class,
            "status": e.status,
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "reason": e.reason,
            "is_emergency": e.is_emergency,
            "days_ago": e.days_ago,
        })

    return {
        "demographics": {
            "patient_id": snapshot.patient_id,
            "abha_number": snapshot.abha_number,
            "abha_address": snapshot.abha_address,
            "name": snapshot.name,
            "gender": snapshot.gender,
            "date_of_birth": snapshot.date_of_birth.isoformat(),
            "age": snapshot.age,
            "phone": snapshot.phone,
            "address": snapshot.address,
            "city": snapshot.city,
            "state": snapshot.state,
        },
        "conditions": conditions,
        "medications": medications,
        "allergies": allergies,
        "recent_vitals": vitals,
        "recent_encounters": encounters,
        "hints": {
            "elderly": snapshot.hints.elderly,
            "pediatric": snapshot.hints.pediatric,
            "cardiac_history": snapshot.hints.cardiac_history,
            "respiratory_history": snapshot.hints.respiratory_history,
            "diabetic": snapshot.hints.diabetic,
            "polypharmacy": snapshot.hints.polypharmacy,
            "recent_ed_visit": snapshot.hints.recent_ed_visit,
            "high_risk_conditions": snapshot.hints.high_risk_conditions,
            "allergy_count": snapshot.hints.allergy_count,
            "immunocompromised": snapshot.hints.immunocompromised,
            "active_condition_count": snapshot.hints.active_condition_count,
            "active_medication_count": snapshot.hints.active_medication_count,
        },
        "summary": {
            "active_conditions": snapshot.hints.active_condition_count,
            "active_medications": snapshot.hints.active_medication_count,
            "total_allergies": snapshot.hints.allergy_count,
            "recent_encounters": len(encounters),
        },
    }
