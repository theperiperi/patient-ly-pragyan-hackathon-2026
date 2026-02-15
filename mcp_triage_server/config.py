"""Configuration for MCP Triage Server."""

from pathlib import Path

# Data paths
PROJECT_ROOT = Path(__file__).parent.parent
SEED_DATA_DIR = PROJECT_ROOT / "abdm-local-dev-kit" / "data" / "seed"
FHIR_BUNDLES_DIR = SEED_DATA_DIR / "fhir_bundles"
PATIENTS_INDEX_FILE = SEED_DATA_DIR / "patients.json"

# High-risk condition keywords for hint generation
HIGH_RISK_CONDITIONS = [
    "diabetes",
    "hypertension",
    "heart failure",
    "cardiac",
    "copd",
    "chronic obstructive",
    "asthma",
    "renal",
    "kidney",
    "liver",
    "cirrhosis",
    "cancer",
    "malignant",
    "stroke",
    "cerebrovascular",
    "hiv",
    "immunodeficiency",
]

CARDIAC_CONDITIONS = [
    "heart",
    "cardiac",
    "coronary",
    "myocardial",
    "atrial",
    "ventricular",
    "angina",
    "arrhythmia",
]

RESPIRATORY_CONDITIONS = [
    "copd",
    "asthma",
    "pneumonia",
    "bronchitis",
    "respiratory",
    "pulmonary",
    "lung",
]

IMMUNOCOMPROMISING_CONDITIONS = [
    "hiv",
    "aids",
    "immunodeficiency",
    "leukemia",
    "lymphoma",
    "transplant",
    "chemotherapy",
]

# Age thresholds
ELDERLY_AGE = 65
PEDIATRIC_AGE = 18

# Polypharmacy threshold
POLYPHARMACY_THRESHOLD = 5

# Recent encounter threshold (days)
RECENT_ED_DAYS = 30
