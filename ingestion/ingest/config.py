"""Constants and configuration for the Patient.ly FHIR ingestion pipeline."""

# --- FHIR Systems ---
LOINC_SYSTEM = "http://loinc.org"
SNOMED_SYSTEM = "http://snomed.info/sct"
UCUM_SYSTEM = "http://unitsofmeasure.org"
ICD10_SYSTEM = "http://hl7.org/fhir/sid/icd-10"
OBSERVATION_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/observation-category"
CONDITION_CLINICAL_SYSTEM = "http://terminology.hl7.org/CodeSystem/condition-clinical"
CONDITION_VERIFICATION_SYSTEM = "http://terminology.hl7.org/CodeSystem/condition-ver-status"
CONDITION_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/condition-category"
ENCOUNTER_CLASS_SYSTEM = "http://terminology.hl7.org/CodeSystem/v3-ActCode"
DIAGNOSTIC_REPORT_CATEGORY_SYSTEM = "http://terminology.hl7.org/CodeSystem/v2-0074"
DOCUMENT_TYPE_SYSTEM = "http://loinc.org"

# --- ABDM / NRCES India Profiles ---
NRCES_PROFILE_BASE = "https://nrces.in/ndhm/fhir/r4/StructureDefinition"
NRCES_PATIENT_PROFILE = f"{NRCES_PROFILE_BASE}/Patient"
NRCES_OBSERVATION_PROFILE = f"{NRCES_PROFILE_BASE}/ObservationVitalSigns"
ABDM_HEALTH_ID_SYSTEM = "https://healthid.abdm.gov.in"

# --- Vital Signs LOINC Codes: (code, display) ---
LOINC_HEART_RATE = ("8867-4", "Heart rate")
LOINC_SPO2 = ("2708-6", "Oxygen saturation in Arterial blood by Pulse oximetry")
LOINC_BP_PANEL = ("85354-9", "Blood pressure panel with all children optional")
LOINC_BP_SYSTOLIC = ("8480-6", "Systolic blood pressure")
LOINC_BP_DIASTOLIC = ("8462-4", "Diastolic blood pressure")
LOINC_BODY_TEMP = ("8310-5", "Body temperature")
LOINC_RESP_RATE = ("9279-1", "Respiratory rate")
LOINC_BODY_WEIGHT = ("29463-7", "Body weight")
LOINC_BODY_HEIGHT = ("8302-2", "Body height")
LOINC_BMI = ("39156-5", "Body mass index (BMI)")

# --- UCUM Units ---
UCUM_BPM = "/min"
UCUM_PERCENT = "%"
UCUM_MMHG = "mm[Hg]"
UCUM_CELSIUS = "Cel"
UCUM_KG = "kg"
UCUM_CM = "cm"
UCUM_KG_M2 = "kg/m2"

# --- Common SNOMED Codes ---
SNOMED_CHEST_PAIN = ("29857009", "Chest pain")
SNOMED_HYPERTENSION = ("38341003", "Hypertensive disorder")
SNOMED_T2DM = ("44054006", "Diabetes mellitus type 2")
SNOMED_ASTHMA = ("195967001", "Asthma")
SNOMED_COPD = ("13645005", "Chronic obstructive lung disease")
SNOMED_MI = ("22298006", "Myocardial infarction")
SNOMED_EMERGENCY_TRANSPORT = ("50849002", "Emergency room admission")

# --- Apple HealthKit Type Identifiers -> LOINC mapping ---
HEALTHKIT_TO_LOINC = {
    "HKQuantityTypeIdentifierHeartRate": LOINC_HEART_RATE,
    "HKQuantityTypeIdentifierOxygenSaturation": LOINC_SPO2,
    "HKQuantityTypeIdentifierBloodPressureSystolic": LOINC_BP_SYSTOLIC,
    "HKQuantityTypeIdentifierBloodPressureDiastolic": LOINC_BP_DIASTOLIC,
    "HKQuantityTypeIdentifierBodyTemperature": LOINC_BODY_TEMP,
    "HKQuantityTypeIdentifierRespiratoryRate": LOINC_RESP_RATE,
    "HKQuantityTypeIdentifierBodyMass": LOINC_BODY_WEIGHT,
    "HKQuantityTypeIdentifierHeight": LOINC_BODY_HEIGHT,
}

# HealthKit type -> UCUM unit
HEALTHKIT_UNITS = {
    "HKQuantityTypeIdentifierHeartRate": ("beats/minute", UCUM_BPM),
    "HKQuantityTypeIdentifierOxygenSaturation": ("%", UCUM_PERCENT),
    "HKQuantityTypeIdentifierBloodPressureSystolic": ("mmHg", UCUM_MMHG),
    "HKQuantityTypeIdentifierBloodPressureDiastolic": ("mmHg", UCUM_MMHG),
    "HKQuantityTypeIdentifierBodyTemperature": ("degC", UCUM_CELSIUS),
    "HKQuantityTypeIdentifierRespiratoryRate": ("breaths/minute", UCUM_BPM),
    "HKQuantityTypeIdentifierBodyMass": ("kg", UCUM_KG),
    "HKQuantityTypeIdentifierHeight": ("cm", UCUM_CM),
}

# --- Google Fit dataTypeName -> LOINC mapping ---
GOOGLE_FIT_TO_LOINC = {
    "com.google.heart_rate.bpm": LOINC_HEART_RATE,
    "com.google.oxygen_saturation": LOINC_SPO2,
    "com.google.blood_pressure": LOINC_BP_PANEL,
    "com.google.body.temperature": LOINC_BODY_TEMP,
}

GOOGLE_FIT_UNITS = {
    "com.google.heart_rate.bpm": ("bpm", UCUM_BPM),
    "com.google.oxygen_saturation": ("%", UCUM_PERCENT),
    "com.google.body.temperature": ("degC", UCUM_CELSIUS),
}
