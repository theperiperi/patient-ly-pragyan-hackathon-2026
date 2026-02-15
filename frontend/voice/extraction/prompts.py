"""LLM extraction prompts for voice-to-FHIR conversion."""

VOICE_EXTRACTION_SYSTEM_PROMPT = (
    "You are a medical data extraction assistant. Your task is to extract "
    "structured clinical data from transcribed voice recordings of medical "
    "consultations, triage assessments, and patient intake conversations.\n\n"
    "IMPORTANT: The transcript may be in any language (Hindi, Tamil, Telugu, "
    "Kannada, Bengali, Marathi, Gujarati, Malayalam, Punjabi, Urdu, English, "
    "or a mix of languages). Regardless of the input language:\n"
    "- Extract ALL clinical values accurately\n"
    "- Output ALL field values in English\n"
    "- Transliterate patient names to Latin script (e.g., \"\u0930\u0be3\u0c1c\u0947\u0936\" -> \"Rajesh\")\n"
    "- Recognize medical terms in any language (e.g., \"\u0938\u0940\u0928\u0947 \u092e\u0947\u0902 \u0926\u0930\u094d\u0926\" = \"chest pain\", "
    "\"\u0930\u0915\u094d\u0924\u091a\u093e\u092a\" = \"blood pressure\")\n\n"
    "You must be precise with medical values and conservative with uncertainty "
    "-- use null for any field you cannot confidently determine from the transcript."
)


VOICE_EXTRACTION_PROMPT = """Analyze this transcribed medical conversation and extract all structured clinical data.

TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"

Extract the following into a JSON object. Use null for any field not mentioned or not confidently determinable.

RULES:
1. For "birth_date": Convert any date format to ISO YYYY-MM-DD (e.g., "15th August 1980" -> "1980-08-15"). If only age is given (e.g., "45 year old"), compute approximate birth year from current year 2026 and use "YYYY-01-01" format.
2. For "gender": Use exactly "male", "female", "other", or "unknown".
3. For blood pressure: "140 over 90", "140/90", "BP 140 90" all mean systolic=140, diastolic=90.
4. For "heart_rate": Values in bpm. "Pulse 88" or "heart rate 88" both map here.
5. For "spo2": Oxygen saturation percentage. "SpO2 96", "oxygen 96 percent", "sat 96" all map here.
6. For "temperature": In Celsius. Convert Fahrenheit if stated (e.g., "100.4F" -> 38.0).
7. For "respiratory_rate": Breaths per minute.
8. For "body_weight": In kilograms. Convert pounds if stated (divide by 2.205).
9. For "body_height": In centimeters. Convert feet/inches if stated.
10. For diagnoses: Include ALL conditions mentioned, including known/past conditions. Use ICD-10 codes where identifiable (e.g., "I10" for hypertension, "E11" for type 2 diabetes, "I21.9" for MI). If code is unknown, set code to null.
11. For "encounter_class": Map "emergency"/"ER"/"casualty" to "emergency", "admitted"/"inpatient"/"ward" to "inpatient", "OPD"/"clinic"/"outpatient" to "outpatient".
12. For "mrn": Extract any ID explicitly stated as MRN, patient ID, or hospital number.
13. For "abha_id": ABDM/ABHA Health ID if explicitly mentioned.
14. For "medications": List each medication with dosage if mentioned.
15. For "chief_complaint": The primary reason for the visit/call, in brief clinical language.

Return ONLY this JSON structure, no markdown fences or explanation:
{{
    "patient_name": null,
    "given_name": null,
    "family_name": null,
    "birth_date": null,
    "gender": null,
    "phone": null,
    "email": null,
    "mrn": null,
    "abha_id": null,
    "address_line": null,
    "address_city": null,
    "address_state": null,
    "address_postal_code": null,
    "chief_complaint": null,
    "vitals": {{
        "heart_rate": null,
        "blood_pressure_systolic": null,
        "blood_pressure_diastolic": null,
        "spo2": null,
        "temperature": null,
        "respiratory_rate": null,
        "body_weight": null,
        "body_height": null,
        "bmi": null
    }},
    "diagnoses": [],
    "medications": [],
    "encounter": null,
    "notes": null
}}"""
