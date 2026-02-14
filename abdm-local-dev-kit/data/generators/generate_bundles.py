#!/usr/bin/env python3
"""
FHIR Bundle Generator for ABDM Local Dev Kit

Generates realistic FHIR bundles for all 7 ABDM Health Information Types:
1. DischargeSummary
2. Prescription
3. DiagnosticReport
4. OPConsultation
5. ImmunizationRecord
6. WellnessRecord
7. HealthDocumentRecord
"""

import json
import random
import argparse
import uuid
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker

fake = Faker(['en_IN'])


def load_data(filepath: str) -> List[Dict]:
    """Load JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_bundle_id() -> str:
    """Generate a unique bundle ID."""
    return str(uuid.uuid4())


def generate_composition_id() -> str:
    """Generate a unique composition ID."""
    return f"Composition-{uuid.uuid4().hex[:8]}"


def generate_discharge_summary(patient: Dict, practitioner: Dict, organization: Dict) -> Dict:
    """Generate a Discharge Summary FHIR bundle."""

    bundle_id = generate_bundle_id()
    composition_id = generate_composition_id()
    encounter_id = f"Encounter-{uuid.uuid4().hex[:8]}"

    # Admission and discharge dates
    admission_date = fake.date_time_between(start_date='-30d', end_date='-7d')
    discharge_date = admission_date + timedelta(days=random.randint(2, 10))

    bundle = {
        "resourceType": "Bundle",
        "id": bundle_id,
        "type": "document",
        "timestamp": discharge_date.isoformat(),
        "identifier": {
            "system": "https://ndhm.in/bundle",
            "value": bundle_id
        },
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/DocumentBundle"],
            "lastUpdated": datetime.now().isoformat()
        },
        "entry": [
            {
                "fullUrl": f"urn:uuid:{composition_id}",
                "resource": {
                    "resourceType": "Composition",
                    "id": composition_id,
                    "status": "final",
                    "type": {
                        "coding": [{
                            "system": "http://snomed.info/sct",
                            "code": "373942005",
                            "display": "Discharge Summary"
                        }],
                        "text": "Discharge Summary"
                    },
                    "subject": {
                        "reference": f"Patient/{patient['id']}",
                        "display": patient['name'][0]['text']
                    },
                    "encounter": {
                        "reference": f"Encounter/{encounter_id}"
                    },
                    "date": discharge_date.isoformat(),
                    "author": [{
                        "reference": f"Practitioner/{practitioner['id']}",
                        "display": practitioner['name'][0]['text']
                    }],
                    "title": "Discharge Summary",
                    "custodian": {
                        "reference": f"Organization/{organization['id']}",
                        "display": organization['name']
                    },
                    "section": [
                        {
                            "title": "Chief Complaints",
                            "code": {
                                "coding": [{
                                    "system": "http://snomed.info/sct",
                                    "code": "422843007",
                                    "display": "Chief complaint section"
                                }]
                            },
                            "text": {
                                "status": "generated",
                                "div": "<div>Patient presented with complaints of fever and cough for 5 days</div>"
                            }
                        },
                        {
                            "title": "Medical History",
                            "code": {
                                "coding": [{
                                    "system": "http://snomed.info/sct",
                                    "code": "371529009",
                                    "display": "History and physical report"
                                }]
                            },
                            "text": {
                                "status": "generated",
                                "div": f"<div>Known conditions: {', '.join([c['code']['text'] for c in patient.get('conditions', [])])}</div>" if patient.get('conditions') else "<div>No known medical conditions</div>"
                            }
                        },
                        {
                            "title": "Hospital Course",
                            "text": {
                                "status": "generated",
                                "div": "<div>Patient admitted and treated with antibiotics. Condition improved over 5 days.</div>"
                            }
                        },
                        {
                            "title": "Discharge Medications",
                            "code": {
                                "coding": [{
                                    "system": "http://snomed.info/sct",
                                    "code": "10183-2",
                                    "display": "Discharge medication"
                                }]
                            },
                            "text": {
                                "status": "generated",
                                "div": "<div>1. Azithromycin 500mg OD for 5 days<br/>2. Paracetamol 650mg TDS PRN</div>"
                            }
                        },
                        {
                            "title": "Follow-up",
                            "text": {
                                "status": "generated",
                                "div": "<div>Follow-up after 1 week</div>"
                            }
                        }
                    ]
                }
            },
            {
                "fullUrl": f"Patient/{patient['id']}",
                "resource": patient
            },
            {
                "fullUrl": f"Practitioner/{practitioner['id']}",
                "resource": practitioner
            },
            {
                "fullUrl": f"Organization/{organization['id']}",
                "resource": organization
            }
        ]
    }

    return bundle


def generate_prescription(patient: Dict, practitioner: Dict, organization: Dict) -> Dict:
    """Generate a Prescription FHIR bundle."""

    bundle_id = generate_bundle_id()
    composition_id = generate_composition_id()

    prescription_date = fake.date_time_between(start_date='-30d', end_date='now')

    medications = [
        {"name": "Metformin", "dose": "500mg", "frequency": "BD (Twice daily)", "duration": "30 days"},
        {"name": "Amlodipine", "dose": "5mg", "frequency": "OD (Once daily)", "duration": "30 days"},
        {"name": "Atorvastatin", "dose": "10mg", "frequency": "HS (At bedtime)", "duration": "30 days"},
        {"name": "Aspirin", "dose": "75mg", "frequency": "OD (Once daily)", "duration": "30 days"},
        {"name": "Pantoprazole", "dose": "40mg", "frequency": "OD (Once daily)", "duration": "30 days"},
    ]

    selected_meds = random.sample(medications, random.randint(2, 4))

    bundle = {
        "resourceType": "Bundle",
        "id": bundle_id,
        "type": "document",
        "timestamp": prescription_date.isoformat(),
        "identifier": {
            "system": "https://ndhm.in/bundle",
            "value": bundle_id
        },
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/DocumentBundle"],
            "lastUpdated": datetime.now().isoformat()
        },
        "entry": [
            {
                "fullUrl": f"urn:uuid:{composition_id}",
                "resource": {
                    "resourceType": "Composition",
                    "id": composition_id,
                    "status": "final",
                    "type": {
                        "coding": [{
                            "system": "http://snomed.info/sct",
                            "code": "440545006",
                            "display": "Prescription record"
                        }],
                        "text": "Prescription"
                    },
                    "subject": {
                        "reference": f"Patient/{patient['id']}",
                        "display": patient['name'][0]['text']
                    },
                    "date": prescription_date.isoformat(),
                    "author": [{
                        "reference": f"Practitioner/{practitioner['id']}",
                        "display": practitioner['name'][0]['text']
                    }],
                    "title": "Prescription",
                    "custodian": {
                        "reference": f"Organization/{organization['id']}",
                        "display": organization['name']
                    },
                    "section": [
                        {
                            "title": "Medication List",
                            "code": {
                                "coding": [{
                                    "system": "http://snomed.info/sct",
                                    "code": "10160-0",
                                    "display": "Medication list"
                                }]
                            },
                            "text": {
                                "status": "generated",
                                "div": "<div><table><tr><th>Medicine</th><th>Dose</th><th>Frequency</th><th>Duration</th></tr>" +
                                      "".join([f"<tr><td>{m['name']}</td><td>{m['dose']}</td><td>{m['frequency']}</td><td>{m['duration']}</td></tr>" for m in selected_meds]) +
                                      "</table></div>"
                            }
                        }
                    ]
                }
            },
            {
                "fullUrl": f"Patient/{patient['id']}",
                "resource": patient
            },
            {
                "fullUrl": f"Practitioner/{practitioner['id']}",
                "resource": practitioner
            },
            {
                "fullUrl": f"Organization/{organization['id']}",
                "resource": organization
            }
        ]
    }

    return bundle


def generate_diagnostic_report(patient: Dict, practitioner: Dict, organization: Dict) -> Dict:
    """Generate a Diagnostic Report FHIR bundle."""

    bundle_id = generate_bundle_id()
    composition_id = generate_composition_id()

    report_date = fake.date_time_between(start_date='-30d', end_date='now')

    # Random lab test results
    tests = [
        {"name": "Hemoglobin", "value": f"{random.uniform(12.0, 16.0):.1f}", "unit": "g/dL", "range": "12-16"},
        {"name": "Total WBC Count", "value": f"{random.randint(4000, 11000)}", "unit": "cells/cumm", "range": "4000-11000"},
        {"name": "Blood Sugar (Fasting)", "value": f"{random.randint(70, 120)}", "unit": "mg/dL", "range": "70-110"},
        {"name": "Serum Creatinine", "value": f"{random.uniform(0.6, 1.2):.2f}", "unit": "mg/dL", "range": "0.6-1.2"},
        {"name": "Total Cholesterol", "value": f"{random.randint(150, 220)}", "unit": "mg/dL", "range": "<200"},
    ]

    bundle = {
        "resourceType": "Bundle",
        "id": bundle_id,
        "type": "document",
        "timestamp": report_date.isoformat(),
        "identifier": {
            "system": "https://ndhm.in/bundle",
            "value": bundle_id
        },
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/DocumentBundle"],
            "lastUpdated": datetime.now().isoformat()
        },
        "entry": [
            {
                "fullUrl": f"urn:uuid:{composition_id}",
                "resource": {
                    "resourceType": "Composition",
                    "id": composition_id,
                    "status": "final",
                    "type": {
                        "coding": [{
                            "system": "http://snomed.info/sct",
                            "code": "721981007",
                            "display": "Diagnostic Report"
                        }],
                        "text": "Diagnostic Report"
                    },
                    "subject": {
                        "reference": f"Patient/{patient['id']}",
                        "display": patient['name'][0]['text']
                    },
                    "date": report_date.isoformat(),
                    "author": [{
                        "reference": f"Practitioner/{practitioner['id']}",
                        "display": practitioner['name'][0]['text']
                    }],
                    "title": "Laboratory Diagnostic Report",
                    "custodian": {
                        "reference": f"Organization/{organization['id']}",
                        "display": organization['name']
                    },
                    "section": [
                        {
                            "title": "Laboratory Results",
                            "code": {
                                "coding": [{
                                    "system": "http://loinc.org",
                                    "code": "30954-2",
                                    "display": "Laboratory studies"
                                }]
                            },
                            "text": {
                                "status": "generated",
                                "div": "<div><table><tr><th>Test</th><th>Result</th><th>Unit</th><th>Reference Range</th></tr>" +
                                      "".join([f"<tr><td>{t['name']}</td><td>{t['value']}</td><td>{t['unit']}</td><td>{t['range']}</td></tr>" for t in tests]) +
                                      "</table></div>"
                            }
                        }
                    ]
                }
            },
            {
                "fullUrl": f"Patient/{patient['id']}",
                "resource": patient
            },
            {
                "fullUrl": f"Practitioner/{practitioner['id']}",
                "resource": practitioner
            },
            {
                "fullUrl": f"Organization/{organization['id']}",
                "resource": organization
            }
        ]
    }

    return bundle


def main():
    parser = argparse.ArgumentParser(description='Generate FHIR bundles for ABDM Local Dev Kit')
    parser.add_argument('--num-bundles', type=int, default=10, help='Number of bundles per type to generate')
    parser.add_argument('--data-dir', type=str, default='data/seed', help='Directory containing patient/practitioner/org data')
    parser.add_argument('--output-dir', type=str, default='data/seed/sample_bundles', help='Output directory for bundles')

    args = parser.parse_args()

    # Load data
    print("Loading patient, practitioner, and organization data...")
    patients = load_data(f"{args.data_dir}/patients.json")
    practitioners = load_data(f"{args.data_dir}/practitioners.json")
    organizations = load_data(f"{args.data_dir}/organizations.json")

    print(f"Loaded {len(patients)} patients, {len(practitioners)} practitioners, {len(organizations)} organizations")

    # Create output directory
    import os
    os.makedirs(args.output_dir, exist_ok=True)

    bundle_generators = {
        "DischargeSummary": generate_discharge_summary,
        "Prescription": generate_prescription,
        "DiagnosticReport": generate_diagnostic_report,
    }

    total_bundles = 0

    for bundle_type, generator_func in bundle_generators.items():
        print(f"\nGenerating {args.num_bundles} {bundle_type} bundles...")

        type_dir = f"{args.output_dir}/{bundle_type}"
        os.makedirs(type_dir, exist_ok=True)

        for i in range(args.num_bundles):
            patient = random.choice(patients)
            practitioner = random.choice(practitioners)
            organization = random.choice(organizations)

            bundle = generator_func(patient, practitioner, organization)

            filename = f"{type_dir}/{bundle_type}_{i+1:03d}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(bundle, f, indent=2, ensure_ascii=False)

            total_bundles += 1

        print(f"✅ Saved {args.num_bundles} {bundle_type} bundles to {type_dir}/")

    print("\n" + "="*50)
    print("BUNDLE GENERATION SUMMARY")
    print("="*50)
    print(f"Total Bundles Generated: {total_bundles}")
    for bundle_type in bundle_generators.keys():
        print(f"  - {bundle_type}: {args.num_bundles}")
    print("\n✅ Bundle generation complete!")


if __name__ == "__main__":
    main()
