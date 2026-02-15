"""Clinical history tools."""

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


def get_conditions(
    patient_id: str,
    status: Optional[str] = None,
) -> dict:
    """
    Get patient conditions (diagnoses).

    Args:
        patient_id: Patient ID or ABHA address
        status: Filter by clinical status (active, resolved, etc.)

    Returns:
        Dictionary with conditions list
    """
    resolved_id = _resolve_patient_id(patient_id)
    if not resolved_id:
        return {"error": f"Patient not found: {patient_id}"}

    extractor = get_extractor()
    conditions = extractor.extract_conditions(resolved_id)

    # Apply status filter
    if status:
        conditions = [c for c in conditions if c.clinical_status.lower() == status.lower()]

    # Convert to dict
    condition_list = []
    for c in conditions:
        condition_list.append({
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

    active_count = sum(1 for c in conditions if c.clinical_status == "active")
    return {
        "patient_id": resolved_id,
        "total": len(condition_list),
        "active_count": active_count,
        "conditions": condition_list,
    }


def get_medications(
    patient_id: str,
    status: Optional[str] = None,
) -> dict:
    """
    Get patient medications.

    Args:
        patient_id: Patient ID or ABHA address
        status: Filter by status (active, completed, etc.)

    Returns:
        Dictionary with medications list
    """
    resolved_id = _resolve_patient_id(patient_id)
    if not resolved_id:
        return {"error": f"Patient not found: {patient_id}"}

    extractor = get_extractor()
    medications = extractor.extract_medications(resolved_id)

    # Apply status filter
    if status:
        medications = [m for m in medications if m.status.lower() == status.lower()]

    # Convert to dict
    medication_list = []
    for m in medications:
        medication_list.append({
            "code": m.code,
            "display": m.display,
            "status": m.status,
            "dosage": m.dosage,
            "start_date": m.start_date.isoformat() if m.start_date else None,
        })

    active_count = sum(1 for m in medications if m.status == "active")
    return {
        "patient_id": resolved_id,
        "total": len(medication_list),
        "active_count": active_count,
        "medications": medication_list,
    }


def get_allergies(patient_id: str) -> dict:
    """
    Get patient allergies.

    Args:
        patient_id: Patient ID or ABHA address

    Returns:
        Dictionary with allergies list
    """
    resolved_id = _resolve_patient_id(patient_id)
    if not resolved_id:
        return {"error": f"Patient not found: {patient_id}"}

    extractor = get_extractor()
    allergies = extractor.extract_allergies(resolved_id)

    # Convert to dict
    allergy_list = []
    for a in allergies:
        allergy_list.append({
            "code": a.code,
            "display": a.display,
            "category": a.category,
            "criticality": a.criticality,
            "reaction_type": a.reaction_type,
        })

    # Count by criticality
    high_criticality = sum(1 for a in allergies if a.criticality == "high")
    return {
        "patient_id": resolved_id,
        "total": len(allergy_list),
        "high_criticality_count": high_criticality,
        "allergies": allergy_list,
    }


def get_vitals(
    patient_id: str,
    limit: int = 20,
) -> dict:
    """
    Get patient vital signs.

    Args:
        patient_id: Patient ID or ABHA address
        limit: Maximum vitals to return

    Returns:
        Dictionary with vitals list
    """
    resolved_id = _resolve_patient_id(patient_id)
    if not resolved_id:
        return {"error": f"Patient not found: {patient_id}"}

    extractor = get_extractor()
    vitals = extractor.extract_vitals(resolved_id, limit=limit)

    # Convert to dict
    vital_list = []
    for v in vitals:
        vital_list.append({
            "code": v.code,
            "display": v.display,
            "value": v.value,
            "unit": v.unit,
            "recorded_date": v.recorded_date.isoformat() if v.recorded_date else None,
        })

    return {
        "patient_id": resolved_id,
        "count": len(vital_list),
        "vitals": vital_list,
    }


def get_encounters(
    patient_id: str,
    days_back: int = 365,
    limit: int = 20,
) -> dict:
    """
    Get patient encounters (healthcare visits).

    Args:
        patient_id: Patient ID or ABHA address
        days_back: Look back period in days (0 = all time)
        limit: Maximum encounters to return

    Returns:
        Dictionary with encounters list
    """
    resolved_id = _resolve_patient_id(patient_id)
    if not resolved_id:
        return {"error": f"Patient not found: {patient_id}"}

    extractor = get_extractor()
    encounters = extractor.extract_encounters(resolved_id, days_back=days_back)

    # Apply limit
    encounters = encounters[:limit]

    # Convert to dict
    encounter_list = []
    for e in encounters:
        encounter_list.append({
            "encounter_id": e.encounter_id,
            "encounter_type": e.encounter_type,
            "encounter_class": e.encounter_class,
            "status": e.status,
            "start_date": e.start_date.isoformat() if e.start_date else None,
            "reason": e.reason,
            "is_emergency": e.is_emergency,
            "days_ago": e.days_ago,
        })

    # Count emergencies
    emergency_count = sum(1 for e in encounters if e.is_emergency)
    return {
        "patient_id": resolved_id,
        "days_back": days_back,
        "count": len(encounter_list),
        "emergency_count": emergency_count,
        "encounters": encounter_list,
    }
