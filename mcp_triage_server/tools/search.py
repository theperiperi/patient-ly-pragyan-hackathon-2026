"""Patient search tools."""

from typing import Optional

from ..data.loader import get_loader
from ..data.extractor import get_extractor


def search_patients(
    query: str,
    gender: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    limit: int = 20,
) -> dict:
    """
    Search patients by name, ABHA number, or ABHA address.

    Args:
        query: Search query (name, ABHA number, or ABHA address)
        gender: Filter by gender (M, F)
        min_age: Minimum age filter
        max_age: Maximum age filter
        limit: Maximum results to return

    Returns:
        Dictionary with matching patients list
    """
    loader = get_loader()
    extractor = get_extractor()

    # Search in patient index
    matches = loader.search_patients(query)

    results = []
    for match in matches:
        abha_addr = match.get("abhaAddress", "")
        patient_id = loader.abha_to_id.get(abha_addr)

        if not patient_id:
            continue

        # Get basic info for filtering
        basic = extractor.extract_patient_basic(patient_id)
        if not basic:
            continue

        # Apply filters
        if gender and basic.gender.upper() != gender.upper():
            continue
        if min_age is not None and basic.age < min_age:
            continue
        if max_age is not None and basic.age > max_age:
            continue

        results.append({
            "patient_id": basic.patient_id,
            "abha_number": basic.abha_number,
            "abha_address": basic.abha_address,
            "name": basic.name,
            "gender": basic.gender,
            "age": basic.age,
            "date_of_birth": basic.date_of_birth.isoformat(),
            "city": basic.city,
            "state": basic.state,
        })

        if len(results) >= limit:
            break

    return {
        "query": query,
        "filters": {
            "gender": gender,
            "min_age": min_age,
            "max_age": max_age,
        },
        "count": len(results),
        "patients": results,
    }


def list_patients(
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """
    List all patients in the system.

    Args:
        limit: Maximum patients to return
        offset: Offset for pagination

    Returns:
        Dictionary with patient list and count
    """
    loader = get_loader()
    extractor = get_extractor()

    all_patient_ids = loader.get_all_patient_ids()
    total = len(all_patient_ids)

    # Apply pagination
    patient_ids = all_patient_ids[offset:offset + limit]

    patients = []
    for patient_id in patient_ids:
        basic = extractor.extract_patient_basic(patient_id)
        if basic:
            patients.append({
                "patient_id": basic.patient_id,
                "abha_number": basic.abha_number,
                "abha_address": basic.abha_address,
                "name": basic.name,
                "gender": basic.gender,
                "age": basic.age,
                "date_of_birth": basic.date_of_birth.isoformat(),
                "city": basic.city,
                "state": basic.state,
            })

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "count": len(patients),
        "patients": patients,
    }
