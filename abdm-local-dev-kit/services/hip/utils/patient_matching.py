"""
Patient Matching Utilities

Fuzzy matching logic for patient discovery based on demographics.
"""

import re
from typing import Optional, Dict, List
from difflib import SequenceMatcher


def normalize_phone(phone: str) -> str:
    """
    Normalize phone number for matching.

    Args:
        phone: Phone number in any format

    Returns:
        Normalized 10-digit phone number
    """
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)

    # Get last 10 digits (removes country code)
    if len(digits) >= 10:
        return digits[-10:]
    return digits


def normalize_name(name: str) -> str:
    """
    Normalize name for matching.

    Args:
        name: Full name

    Returns:
        Normalized name (lowercase, no extra spaces)
    """
    return ' '.join(name.lower().split())


def similarity_score(str1: str, str2: str) -> float:
    """
    Calculate similarity score between two strings.

    Args:
        str1: First string
        str2: Second string

    Returns:
        Similarity score between 0.0 and 1.0
    """
    return SequenceMatcher(None, normalize_name(str1), normalize_name(str2)).ratio()


def match_by_abha(patient: Dict, abha_number: str) -> bool:
    """
    Match patient by ABHA number (exact match).

    Args:
        patient: Patient document from database
        abha_number: ABHA number to match

    Returns:
        True if matches
    """
    return patient.get('abha_number') == abha_number


def match_by_phone(patient: Dict, phone: str) -> bool:
    """
    Match patient by phone number.

    Args:
        patient: Patient document
        phone: Phone number to match

    Returns:
        True if matches
    """
    normalized_search = normalize_phone(phone)

    for telecom in patient.get('telecom', []):
        if telecom.get('system') == 'phone':
            patient_phone = normalize_phone(telecom.get('value', ''))
            if patient_phone == normalized_search:
                return True

    return False


def match_by_demographics(
    patient: Dict,
    name: Optional[str] = None,
    gender: Optional[str] = None,
    year_of_birth: Optional[int] = None
) -> float:
    """
    Match patient by demographics with fuzzy matching.

    Args:
        patient: Patient document
        name: Patient name
        gender: Patient gender
        year_of_birth: Year of birth

    Returns:
        Match score between 0.0 and 1.0
    """
    score = 0.0
    criteria_count = 0

    # Name matching (weighted most heavily)
    if name:
        criteria_count += 1
        patient_name = patient.get('name', [{}])[0].get('text', '')
        name_score = similarity_score(patient_name, name)
        score += name_score * 0.6  # 60% weight on name

    # Gender matching (exact)
    if gender:
        criteria_count += 1
        if patient.get('gender', '').lower() == gender.lower():
            score += 0.2  # 20% weight

    # Year of birth matching (exact)
    if year_of_birth:
        criteria_count += 1
        birth_date = patient.get('birthDate', '')
        if birth_date and birth_date.startswith(str(year_of_birth)):
            score += 0.2  # 20% weight

    # Normalize score based on criteria provided
    if criteria_count > 0:
        return min(score, 1.0)
    return 0.0


def find_matching_patients(
    patients: List[Dict],
    abha_number: Optional[str] = None,
    phone: Optional[str] = None,
    name: Optional[str] = None,
    gender: Optional[str] = None,
    year_of_birth: Optional[int] = None,
    threshold: float = 0.7
) -> List[Dict]:
    """
    Find matching patients from a list.

    Args:
        patients: List of patient documents
        abha_number: ABHA number (exact match if provided)
        phone: Phone number
        name: Patient name
        gender: Patient gender
        year_of_birth: Year of birth
        threshold: Minimum match score for demographics (default 0.7)

    Returns:
        List of matching patients with match scores
    """
    matches = []

    for patient in patients:
        match_data = {"patient": patient, "score": 0.0, "match_type": ""}

        # Exact ABHA match has highest priority
        if abha_number and match_by_abha(patient, abha_number):
            match_data["score"] = 1.0
            match_data["match_type"] = "abha"
            matches.append(match_data)
            continue

        # Phone match
        if phone and match_by_phone(patient, phone):
            match_data["score"] = 0.95
            match_data["match_type"] = "phone"
            matches.append(match_data)
            continue

        # Demographics fuzzy match
        if name or gender or year_of_birth:
            demo_score = match_by_demographics(patient, name, gender, year_of_birth)
            if demo_score >= threshold:
                match_data["score"] = demo_score
                match_data["match_type"] = "demographics"
                matches.append(match_data)

    # Sort by score descending
    matches.sort(key=lambda x: x["score"], reverse=True)

    return matches
