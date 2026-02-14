"""Base simulator and shared patient profile."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class PatientProfile:
    """Shared patient profile used by all simulators for coherence."""
    name: str = "Rajesh Kumar"
    given_name: str = "Rajesh"
    family_name: str = "Kumar"
    dob: str = "1975-08-15"
    gender: str = "male"
    mrn: str = "MRN-2024-001234"
    abha_id: str = "ABHA-14-7689-2345-6701"
    phone: str = "+919876543210"
    address: str = "12 MG Road, New Delhi"


@dataclass
class ClinicalScenario:
    """Defines the clinical scenario for coherent data generation."""
    name: str = "chest_pain"
    chief_complaint: str = "Chest pain radiating to left arm, onset 2 hours ago"
    diagnoses: list[dict] = field(default_factory=lambda: [
        {"code": "I21.9", "display": "Acute myocardial infarction, unspecified"},
        {"code": "I10", "display": "Essential hypertension"},
    ])
    baseline_hr: float = 102
    baseline_bp_sys: float = 158
    baseline_bp_dia: float = 94
    baseline_spo2: float = 95
    baseline_temp: float = 37.2
    baseline_rr: float = 22
    vital_trend: str = "improving"
    labs: list[dict] = field(default_factory=lambda: [
        {"name": "Troponin T", "code": "6598-7", "value": 0.85, "unit": "ng/mL", "ref_low": 0.0, "ref_high": 0.04},
        {"name": "Hemoglobin", "code": "718-7", "value": 13.2, "unit": "g/dL", "ref_low": 12.0, "ref_high": 16.0},
        {"name": "WBC", "code": "6690-2", "value": 11.2, "unit": "10*3/uL", "ref_low": 4.5, "ref_high": 11.0},
        {"name": "Glucose", "code": "2345-7", "value": 142, "unit": "mg/dL", "ref_low": 70, "ref_high": 100},
        {"name": "Creatinine", "code": "2160-0", "value": 1.1, "unit": "mg/dL", "ref_low": 0.7, "ref_high": 1.3},
        {"name": "Sodium", "code": "2951-2", "value": 140, "unit": "mmol/L", "ref_low": 136, "ref_high": 145},
        {"name": "Potassium", "code": "2823-3", "value": 4.2, "unit": "mmol/L", "ref_low": 3.5, "ref_high": 5.0},
    ])
    medications: list[str] = field(default_factory=lambda: [
        "Aspirin 325mg stat", "Nitroglycerin 0.4mg SL", "Heparin 5000 IU IV"
    ])


SCENARIOS = {
    "chest_pain": ClinicalScenario(),
    "respiratory_distress": ClinicalScenario(
        name="respiratory_distress",
        chief_complaint="Acute shortness of breath with wheezing",
        diagnoses=[
            {"code": "J45.9", "display": "Asthma, unspecified"},
            {"code": "J96.0", "display": "Acute respiratory failure"},
        ],
        baseline_hr=110, baseline_bp_sys=135, baseline_bp_dia=85,
        baseline_spo2=88, baseline_temp=37.0, baseline_rr=30,
        vital_trend="improving",
        labs=[
            {"name": "WBC", "code": "6690-2", "value": 12.5, "unit": "10*3/uL", "ref_low": 4.5, "ref_high": 11.0},
            {"name": "Hemoglobin", "code": "718-7", "value": 14.0, "unit": "g/dL", "ref_low": 12.0, "ref_high": 16.0},
        ],
        medications=["Salbutamol nebulization", "Hydrocortisone 100mg IV", "O2 at 4L/min"],
    ),
    "diabetic_emergency": ClinicalScenario(
        name="diabetic_emergency",
        chief_complaint="Altered sensorium, polyuria, polydipsia for 2 days",
        diagnoses=[
            {"code": "E11.65", "display": "Type 2 diabetes mellitus with hyperglycemia"},
            {"code": "E87.2", "display": "Acidosis"},
        ],
        baseline_hr=115, baseline_bp_sys=100, baseline_bp_dia=65,
        baseline_spo2=97, baseline_temp=37.5, baseline_rr=28,
        vital_trend="improving",
        labs=[
            {"name": "Glucose", "code": "2345-7", "value": 480, "unit": "mg/dL", "ref_low": 70, "ref_high": 100},
            {"name": "Sodium", "code": "2951-2", "value": 128, "unit": "mmol/L", "ref_low": 136, "ref_high": 145},
            {"name": "Potassium", "code": "2823-3", "value": 5.8, "unit": "mmol/L", "ref_low": 3.5, "ref_high": 5.0},
            {"name": "Creatinine", "code": "2160-0", "value": 1.8, "unit": "mg/dL", "ref_low": 0.7, "ref_high": 1.3},
        ],
        medications=["Insulin drip 0.1 U/kg/hr", "NS 1L bolus", "KCl 20 mEq IV"],
    ),
    "trauma": ClinicalScenario(
        name="trauma",
        chief_complaint="Road traffic accident - motorcycle vs car, multiple injuries",
        diagnoses=[
            {"code": "S06.0", "display": "Concussion"},
            {"code": "S52.5", "display": "Fracture of lower end of radius"},
        ],
        baseline_hr=120, baseline_bp_sys=95, baseline_bp_dia=60,
        baseline_spo2=93, baseline_temp=36.5, baseline_rr=26,
        vital_trend="stable",
        labs=[
            {"name": "Hemoglobin", "code": "718-7", "value": 9.5, "unit": "g/dL", "ref_low": 12.0, "ref_high": 16.0},
            {"name": "WBC", "code": "6690-2", "value": 15.0, "unit": "10*3/uL", "ref_low": 4.5, "ref_high": 11.0},
            {"name": "Platelet", "code": "777-3", "value": 180, "unit": "10*3/uL", "ref_low": 150, "ref_high": 400},
        ],
        medications=["Morphine 4mg IV", "Tetanus toxoid", "NS 2L bolus"],
    ),
}


class BaseSimulator(ABC):
    """Base class for all data simulators."""

    @abstractmethod
    def generate(self, profile: PatientProfile, scenario: ClinicalScenario, output_dir: Path) -> Path:
        """Generate sample data file(s). Returns path to the primary output file."""
        ...
