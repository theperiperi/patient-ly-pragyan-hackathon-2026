#!/usr/bin/env python3
"""
Indian Patient Data Generator for ABDM Local Dev Kit

Generates realistic Indian patient data with:
- ABHA numbers (14-digit format: XX-XXXX-XXXX-XXXX)
- Indian names (regional diversity)
- Indian phone numbers (+91-XXXXXXXXXX)
- Indian addresses (real cities, PIN codes)
- Common Indian health conditions
"""

import json
import random
import argparse
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker

# Initialize Faker with Indian locale
fake = Faker(['en_IN', 'hi_IN'])

# Indian cities with their states and PIN code ranges
INDIAN_CITIES = [
    {"city": "Mumbai", "state": "Maharashtra", "pin_prefix": "40"},
    {"city": "Delhi", "state": "Delhi", "pin_prefix": "11"},
    {"city": "Bangalore", "state": "Karnataka", "pin_prefix": "56"},
    {"city": "Hyderabad", "state": "Telangana", "pin_prefix": "50"},
    {"city": "Chennai", "state": "Tamil Nadu", "pin_prefix": "60"},
    {"city": "Kolkata", "state": "West Bengal", "pin_prefix": "70"},
    {"city": "Pune", "state": "Maharashtra", "pin_prefix": "41"},
    {"city": "Ahmedabad", "state": "Gujarat", "pin_prefix": "38"},
    {"city": "Jaipur", "state": "Rajasthan", "pin_prefix": "30"},
    {"city": "Lucknow", "state": "Uttar Pradesh", "pin_prefix": "22"},
    {"city": "Kochi", "state": "Kerala", "pin_prefix": "68"},
    {"city": "Chandigarh", "state": "Chandigarh", "pin_prefix": "16"},
    {"city": "Indore", "state": "Madhya Pradesh", "pin_prefix": "45"},
    {"city": "Bhopal", "state": "Madhya Pradesh", "pin_prefix": "46"},
    {"city": "Patna", "state": "Bihar", "pin_prefix": "80"},
]

# Common Indian health conditions with prevalence
INDIAN_CONDITIONS = [
    {"code": "73211009", "display": "Diabetes mellitus", "system": "http://snomed.info/sct"},
    {"code": "38341003", "display": "Hypertension", "system": "http://snomed.info/sct"},
    {"code": "44054006", "display": "Type 2 diabetes mellitus", "system": "http://snomed.info/sct"},
    {"code": "56265001", "display": "Heart disease", "system": "http://snomed.info/sct"},
    {"code": "195967001", "display": "Asthma", "system": "http://snomed.info/sct"},
    {"code": "56717001", "display": "Tuberculosis", "system": "http://snomed.info/sct"},
    {"code": "38822007", "display": "Dengue fever", "system": "http://snomed.info/sct"},
    {"code": "84229001", "display": "Malaria", "system": "http://snomed.info/sct"},
    {"code": "75544007", "display": "Typhoid fever", "system": "http://snomed.info/sct"},
    {"code": "13645005", "display": "Chronic obstructive pulmonary disease", "system": "http://snomed.info/sct"},
    {"code": "399211009", "display": "Chronic kidney disease", "system": "http://snomed.info/sct"},
    {"code": "235856003", "display": "Liver disease", "system": "http://snomed.info/sct"},
]

# Common Indian first names by region
INDIAN_FIRST_NAMES = {
    "North": ["Rajesh", "Priya", "Amit", "Neha", "Vikram", "Anjali", "Rahul", "Pooja", "Sanjay", "Rekha"],
    "South": ["Karthik", "Lakshmi", "Ravi", "Deepa", "Suresh", "Kavita", "Mohan", "Radha", "Kumar", "Meena"],
    "East": ["Sourav", "Mala", "Debasis", "Rina", "Subhas", "Bina", "Tapas", "Sumana", "Arijit", "Payal"],
    "West": ["Kiran", "Nisha", "Ashok", "Jyoti", "Ramesh", "Smita", "Prakash", "Varsha", "Mahesh", "Asha"],
}

# Common Indian surnames
INDIAN_SURNAMES = [
    "Sharma", "Verma", "Patel", "Kumar", "Singh", "Das", "Reddy", "Nair", "Pillai", "Iyer",
    "Gupta", "Joshi", "Desai", "Rao", "Mehta", "Shah", "Agarwal", "Banerjee", "Chatterjee", "Malhotra",
    "Kapoor", "Bhatia", "Sinha", "Mishra", "Pandey", "Jain", "Choudhury", "Mukherjee", "Kulkarni", "Naidu",
]


def generate_abha_number() -> str:
    """Generate a realistic ABHA number (14-digit format: XX-XXXX-XXXX-XXXX)."""
    part1 = random.randint(10, 99)
    part2 = random.randint(1000, 9999)
    part3 = random.randint(1000, 9999)
    part4 = random.randint(1000, 9999)
    return f"{part1}-{part2}-{part3}-{part4}"


def generate_indian_phone() -> str:
    """Generate a realistic Indian phone number (+91-XXXXXXXXXX)."""
    # Valid Indian mobile number prefixes (6, 7, 8, 9)
    prefix = random.choice(['6', '7', '8', '9'])
    rest = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return f"+91-{prefix}{rest}"


def generate_indian_name() -> Dict[str, str]:
    """Generate a realistic Indian name with regional diversity."""
    region = random.choice(list(INDIAN_FIRST_NAMES.keys()))
    first_name = random.choice(INDIAN_FIRST_NAMES[region])
    surname = random.choice(INDIAN_SURNAMES)

    return {
        "text": f"{first_name} {surname}",
        "given": [first_name],
        "family": surname
    }


def generate_indian_address() -> Dict:
    """Generate a realistic Indian address."""
    city_data = random.choice(INDIAN_CITIES)

    # Generate realistic street address
    street_number = random.randint(1, 999)
    street_names = ["MG Road", "Park Street", "Main Road", "Station Road", "Gandhi Nagar",
                    "Nehru Street", "Commercial Street", "Church Road", "Ring Road", "Sector"]
    street = random.choice(street_names)

    # Generate PIN code based on city
    pin_code = f"{city_data['pin_prefix']}{random.randint(10, 99)}{random.randint(10, 99)}"

    return {
        "use": "home",
        "type": "physical",
        "text": f"{street_number}, {street}, {city_data['city']}, {city_data['state']} {pin_code}",
        "line": [f"{street_number}", street],
        "city": city_data["city"],
        "state": city_data["state"],
        "postalCode": pin_code,
        "country": "IN"
    }


def generate_conditions(num_conditions: int = None) -> List[Dict]:
    """Generate random health conditions common in India."""
    if num_conditions is None:
        # Most patients have 0-3 conditions
        num_conditions = random.choices([0, 1, 2, 3], weights=[30, 40, 20, 10])[0]

    if num_conditions == 0:
        return []

    selected = random.sample(INDIAN_CONDITIONS, min(num_conditions, len(INDIAN_CONDITIONS)))

    conditions = []
    for cond in selected:
        onset_date = fake.date_between(start_date='-10y', end_date='today')
        conditions.append({
            "code": {
                "coding": [cond],
                "text": cond["display"]
            },
            "onsetDateTime": onset_date.isoformat(),
            "recordedDate": fake.date_between(start_date=onset_date, end_date='today').isoformat()
        })

    return conditions


def generate_patient() -> Dict:
    """Generate a complete patient record with Indian context."""

    # Generate basic demographics
    gender = random.choice(['male', 'female', 'other'])
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=85)

    # Calculate age
    today = datetime.now().date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    # Generate identifiers
    abha_number = generate_abha_number()

    # Generate contact info
    name = generate_indian_name()
    phone = generate_indian_phone()
    email = f"{name['given'][0].lower()}.{name['family'].lower()}@example.com"

    # Generate address
    address = generate_indian_address()

    # Generate conditions based on age
    if age > 50:
        conditions = generate_conditions(random.randint(1, 3))
    elif age > 30:
        conditions = generate_conditions(random.randint(0, 2))
    else:
        conditions = generate_conditions(random.randint(0, 1))

    # Generate blood group
    blood_group = random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'])

    patient = {
        "resourceType": "Patient",
        "id": abha_number.replace('-', ''),
        "identifier": [
            {
                "use": "official",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "NNIND",
                        "display": "National Person Identifier - India"
                    }],
                    "text": "ABHA Number"
                },
                "system": "https://healthid.ndhm.gov.in",
                "value": abha_number
            }
        ],
        "active": True,
        "name": [name],
        "telecom": [
            {
                "system": "phone",
                "value": phone,
                "use": "mobile"
            },
            {
                "system": "email",
                "value": email,
                "use": "home"
            }
        ],
        "gender": gender,
        "birthDate": birth_date.isoformat(),
        "address": [address],
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"]
        },
        "extension": [
            {
                "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                "valueAge": {
                    "value": age,
                    "unit": "years",
                    "system": "http://unitsofmeasure.org",
                    "code": "a"
                }
            }
        ],
        # Add blood group as a custom extension (common in Indian health records)
        "bloodGroup": blood_group,
        "conditions": conditions,
        "createdAt": datetime.now().isoformat(),
        "abha_number": abha_number
    }

    return patient


def generate_practitioners(count: int = 10) -> List[Dict]:
    """Generate Indian doctor/practitioner data."""
    practitioners = []

    specialties = [
        {"code": "394579002", "display": "Cardiology"},
        {"code": "394582007", "display": "Dermatology"},
        {"code": "394583002", "display": "Endocrinology"},
        {"code": "394584008", "display": "Gastroenterology"},
        {"code": "394585009", "display": "Obstetrics and gynecology"},
        {"code": "394586005", "display": "Gynecology"},
        {"code": "394587001", "display": "Psychiatry"},
        {"code": "394588006", "display": "Pediatric surgery"},
        {"code": "394589003", "display": "Nephrology"},
        {"code": "394591006", "display": "Neurology"},
    ]

    for i in range(count):
        name = generate_indian_name()
        specialty = random.choice(specialties)

        # Generate registration number (Indian Medical Council)
        reg_number = f"MCI-{random.randint(10000, 99999)}"

        practitioner = {
            "resourceType": "Practitioner",
            "id": f"practitioner-{i+1:03d}",
            "identifier": [
                {
                    "use": "official",
                    "system": "https://www.nmc.org.in",
                    "value": reg_number
                }
            ],
            "active": True,
            "name": [{
                "prefix": ["Dr."],
                "text": f"Dr. {name['text']}",
                "given": name['given'],
                "family": name['family']
            }],
            "telecom": [
                {
                    "system": "phone",
                    "value": generate_indian_phone(),
                    "use": "work"
                },
                {
                    "system": "email",
                    "value": f"dr.{name['given'][0].lower()}.{name['family'].lower()}@hospital.in",
                    "use": "work"
                }
            ],
            "gender": random.choice(['male', 'female']),
            "qualification": [
                {
                    "code": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0360",
                            "code": "MD",
                            "display": "Doctor of Medicine"
                        }],
                        "text": "MD"
                    }
                },
                {
                    "code": {
                        "coding": [specialty],
                        "text": specialty['display']
                    }
                }
            ],
            "specialty": specialty
        }

        practitioners.append(practitioner)

    return practitioners


def generate_organizations(count: int = 5) -> List[Dict]:
    """Generate Indian hospital/organization data."""
    hospitals = [
        {"name": "Apollo Hospitals", "city": "Bangalore", "type": "Private"},
        {"name": "Fortis Healthcare", "city": "Delhi", "type": "Private"},
        {"name": "AIIMS", "city": "Delhi", "type": "Government"},
        {"name": "Manipal Hospitals", "city": "Bangalore", "type": "Private"},
        {"name": "Max Healthcare", "city": "Delhi", "type": "Private"},
        {"name": "Tata Memorial Hospital", "city": "Mumbai", "type": "Government"},
        {"name": "Christian Medical College", "city": "Vellore", "type": "Private"},
        {"name": "PGIMER", "city": "Chandigarh", "type": "Government"},
        {"name": "Narayana Health", "city": "Bangalore", "type": "Private"},
        {"name": "Medanta", "city": "Gurugram", "type": "Private"},
    ]

    organizations = []

    for i, hospital in enumerate(hospitals[:count]):
        # Find matching city data
        city_data = next((c for c in INDIAN_CITIES if c['city'] == hospital['city']), INDIAN_CITIES[0])

        org_id = f"org-{i+1:03d}"

        organization = {
            "resourceType": "Organization",
            "id": org_id,
            "identifier": [
                {
                    "use": "official",
                    "system": "https://facility.ndhm.gov.in",
                    "value": f"IN-{org_id.upper()}"
                }
            ],
            "active": True,
            "type": [
                {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                        "code": "prov",
                        "display": "Healthcare Provider"
                    }],
                    "text": hospital['type']
                }
            ],
            "name": hospital['name'],
            "telecom": [
                {
                    "system": "phone",
                    "value": generate_indian_phone(),
                    "use": "work"
                },
                {
                    "system": "email",
                    "value": f"contact@{hospital['name'].lower().replace(' ', '')}.in",
                    "use": "work"
                }
            ],
            "address": [
                {
                    "use": "work",
                    "type": "physical",
                    "city": hospital['city'],
                    "state": city_data['state'],
                    "country": "IN"
                }
            ]
        }

        organizations.append(organization)

    return organizations


def main():
    parser = argparse.ArgumentParser(description='Generate Indian patient data for ABDM Local Dev Kit')
    parser.add_argument('--patients', type=int, default=100, help='Number of patients to generate')
    parser.add_argument('--practitioners', type=int, default=10, help='Number of practitioners to generate')
    parser.add_argument('--organizations', type=int, default=5, help='Number of organizations to generate')
    parser.add_argument('--output-dir', type=str, default='data/seed', help='Output directory for generated data')

    args = parser.parse_args()

    print(f"Generating {args.patients} Indian patient records...")
    patients = [generate_patient() for _ in range(args.patients)]

    print(f"Generating {args.practitioners} practitioner records...")
    practitioners = generate_practitioners(args.practitioners)

    print(f"Generating {args.organizations} organization records...")
    organizations = generate_organizations(args.organizations)

    # Save to JSON files
    import os
    os.makedirs(args.output_dir, exist_ok=True)

    patients_file = f"{args.output_dir}/patients.json"
    with open(patients_file, 'w', encoding='utf-8') as f:
        json.dump(patients, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(patients)} patients to {patients_file}")

    practitioners_file = f"{args.output_dir}/practitioners.json"
    with open(practitioners_file, 'w', encoding='utf-8') as f:
        json.dump(practitioners, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(practitioners)} practitioners to {practitioners_file}")

    organizations_file = f"{args.output_dir}/organizations.json"
    with open(organizations_file, 'w', encoding='utf-8') as f:
        json.dump(organizations, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(organizations)} organizations to {organizations_file}")

    # Print summary statistics
    print("\n" + "="*50)
    print("GENERATION SUMMARY")
    print("="*50)
    print(f"Total Patients: {len(patients)}")
    print(f"  - Male: {sum(1 for p in patients if p['gender'] == 'male')}")
    print(f"  - Female: {sum(1 for p in patients if p['gender'] == 'female')}")
    print(f"  - Other: {sum(1 for p in patients if p['gender'] == 'other')}")
    print(f"\nTotal Practitioners: {len(practitioners)}")
    print(f"Total Organizations: {len(organizations)}")

    # Condition statistics
    all_conditions = []
    for p in patients:
        all_conditions.extend([c['code']['text'] for c in p.get('conditions', [])])

    if all_conditions:
        from collections import Counter
        condition_counts = Counter(all_conditions)
        print(f"\nTop 5 Health Conditions:")
        for condition, count in condition_counts.most_common(5):
            print(f"  - {condition}: {count} patients")

    print("\n✅ Data generation complete!")


if __name__ == "__main__":
    main()
