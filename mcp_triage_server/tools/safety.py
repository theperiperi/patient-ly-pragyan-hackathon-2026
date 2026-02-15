"""Safety check tools."""

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


def lookup_drug_allergies(
    patient_id: str,
    medication: str,
) -> dict:
    """
    Check if a medication conflicts with patient's documented allergies.

    This tool performs a text-based match between the medication name
    and the patient's documented allergies. It's a safety check to help
    identify potential contraindications.

    Args:
        patient_id: Patient ID or ABHA address
        medication: Name of medication to check

    Returns:
        Dictionary with:
        - has_conflict: True if potential allergy conflict found
        - conflicts: List of matching allergies with details
        - patient_allergies: All documented allergies for context
    """
    resolved_id = _resolve_patient_id(patient_id)
    if not resolved_id:
        return {"error": f"Patient not found: {patient_id}"}

    extractor = get_extractor()
    allergies = extractor.extract_allergies(resolved_id)

    medication_lower = medication.lower()

    # Check for conflicts
    conflicts = []
    for allergy in allergies:
        allergy_display = allergy.display.lower()

        # Direct match
        if medication_lower in allergy_display or allergy_display in medication_lower:
            conflicts.append({
                "allergy": allergy.display,
                "category": allergy.category,
                "criticality": allergy.criticality,
                "reaction_type": allergy.reaction_type,
                "match_type": "direct",
            })
            continue

        # Check for common drug class relationships
        # This is a simplified check - real systems would use drug databases
        drug_classes = {
            "penicillin": ["amoxicillin", "ampicillin", "penicillin"],
            "cephalosporin": ["cefazolin", "ceftriaxone", "cephalexin"],
            "sulfa": ["sulfamethoxazole", "sulfasalazine", "trimethoprim-sulfamethoxazole"],
            "nsaid": ["ibuprofen", "naproxen", "aspirin", "celecoxib"],
            "opioid": ["morphine", "codeine", "oxycodone", "hydrocodone"],
            "statin": ["atorvastatin", "simvastatin", "rosuvastatin"],
            "ace inhibitor": ["lisinopril", "enalapril", "ramipril"],
        }

        for drug_class, members in drug_classes.items():
            # Check if allergy is for drug class
            if drug_class in allergy_display:
                # Check if medication is in that class
                if any(m in medication_lower for m in members):
                    conflicts.append({
                        "allergy": allergy.display,
                        "category": allergy.category,
                        "criticality": allergy.criticality,
                        "reaction_type": allergy.reaction_type,
                        "match_type": f"drug_class:{drug_class}",
                    })
                    break

            # Check if allergy is for a specific drug in class
            if any(m in allergy_display for m in members):
                # Cross-check with medication
                if any(m in medication_lower for m in members) or drug_class in medication_lower:
                    conflicts.append({
                        "allergy": allergy.display,
                        "category": allergy.category,
                        "criticality": allergy.criticality,
                        "reaction_type": allergy.reaction_type,
                        "match_type": f"related_drug:{drug_class}",
                    })
                    break

    # Convert all allergies to dict for context
    all_allergies = []
    for a in allergies:
        all_allergies.append({
            "display": a.display,
            "category": a.category,
            "criticality": a.criticality,
            "reaction_type": a.reaction_type,
        })

    return {
        "patient_id": resolved_id,
        "medication_checked": medication,
        "has_conflict": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "patient_allergies": all_allergies,
        "warning": "This is a text-based check. Always verify with clinical judgment and official drug databases." if conflicts else None,
    }
