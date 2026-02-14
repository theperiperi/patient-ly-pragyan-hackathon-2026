#!/usr/bin/env python3
"""
Database Seeding Script for ABDM Local Dev Kit

Seeds MongoDB with generated patient, practitioner, organization data,
and sample FHIR bundles.
"""

import json
import os
import argparse
from pymongo import MongoClient
from datetime import datetime


def load_json_file(filepath: str):
    """Load JSON data from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_bundles_from_directory(directory: str):
    """Load all JSON bundles from a directory."""
    bundles = []
    if not os.path.exists(directory):
        return bundles

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            bundle = load_json_file(filepath)
            bundles.append(bundle)

    return bundles


def seed_database(mongo_uri: str, database_name: str, data_dir: str, bundle_dir: str):
    """Seed the MongoDB database with all generated data."""

    print(f"Connecting to MongoDB: {mongo_uri}")
    client = MongoClient(mongo_uri)
    db = client[database_name]

    # Clear existing data (optional - comment out if you want to preserve existing data)
    print("\nClearing existing data...")
    collections_to_clear = ['patients', 'practitioners', 'organizations', 'health_information_bundles']
    for collection_name in collections_to_clear:
        count = db[collection_name].count_documents({})
        if count > 0:
            db[collection_name].delete_many({})
            print(f"  ✅ Cleared {count} documents from {collection_name}")

    # Load and seed patients
    print("\nSeeding patients...")
    patients_file = os.path.join(data_dir, 'patients.json')
    if os.path.exists(patients_file):
        patients = load_json_file(patients_file)
        if patients:
            result = db.patients.insert_many(patients)
            print(f"  ✅ Inserted {len(result.inserted_ids)} patients")
    else:
        print(f"  ⚠️  Patients file not found: {patients_file}")

    # Load and seed practitioners
    print("\nSeeding practitioners...")
    practitioners_file = os.path.join(data_dir, 'practitioners.json')
    if os.path.exists(practitioners_file):
        practitioners = load_json_file(practitioners_file)
        if practitioners:
            result = db.practitioners.insert_many(practitioners)
            print(f"  ✅ Inserted {len(result.inserted_ids)} practitioners")
    else:
        print(f"  ⚠️  Practitioners file not found: {practitioners_file}")

    # Load and seed organizations
    print("\nSeeding organizations...")
    organizations_file = os.path.join(data_dir, 'organizations.json')
    if os.path.exists(organizations_file):
        organizations = load_json_file(organizations_file)
        if organizations:
            result = db.organizations.insert_many(organizations)
            print(f"  ✅ Inserted {len(result.inserted_ids)} organizations")
    else:
        print(f"  ⚠️  Organizations file not found: {organizations_file}")

    # Load and seed FHIR bundles
    print("\nSeeding FHIR bundles...")
    bundle_types = ['DischargeSummary', 'Prescription', 'DiagnosticReport']

    total_bundles = 0
    for bundle_type in bundle_types:
        type_dir = os.path.join(bundle_dir, bundle_type)
        bundles = load_bundles_from_directory(type_dir)

        if bundles:
            # Add metadata for indexing
            for bundle in bundles:
                # Map FHIR Bundle.id to bundle_id for MongoDB indexing
                bundle['bundle_id'] = bundle.get('id')
                bundle['bundle_type'] = bundle_type
                bundle['created_at'] = datetime.now().isoformat()

                # Extract patient ABHA for easier querying
                for entry in bundle.get('entry', []):
                    resource = entry.get('resource', {})
                    if resource.get('resourceType') == 'Patient':
                        for identifier in resource.get('identifier', []):
                            if 'healthid.ndhm.gov.in' in identifier.get('system', ''):
                                bundle['patient_abha'] = identifier.get('value')
                                break

            result = db.health_information_bundles.insert_many(bundles)
            print(f"  ✅ Inserted {len(result.inserted_ids)} {bundle_type} bundles")
            total_bundles += len(result.inserted_ids)
        else:
            print(f"  ⚠️  No bundles found in {type_dir}")

    # Create indexes for better query performance
    print("\nCreating indexes...")

    # Patient indexes
    db.patients.create_index("abha_number", unique=True)
    db.patients.create_index("id")
    db.patients.create_index([("name.text", "text")])
    print("  ✅ Created patient indexes")

    # Practitioner indexes
    db.practitioners.create_index("id", unique=True)
    db.practitioners.create_index([("name.text", "text")])
    print("  ✅ Created practitioner indexes")

    # Organization indexes
    db.organizations.create_index("id", unique=True)
    db.organizations.create_index("name")
    print("  ✅ Created organization indexes")

    # Bundle indexes
    db.health_information_bundles.create_index("bundle_id")
    db.health_information_bundles.create_index("bundle_type")
    db.health_information_bundles.create_index("patient_abha")
    db.health_information_bundles.create_index("created_at")
    print("  ✅ Created bundle indexes")

    # Print summary
    print("\n" + "="*50)
    print("DATABASE SEEDING SUMMARY")
    print("="*50)
    print(f"Database: {database_name}")
    print(f"Patients: {db.patients.count_documents({})}")
    print(f"Practitioners: {db.practitioners.count_documents({})}")
    print(f"Organizations: {db.organizations.count_documents({})}")
    print(f"FHIR Bundles: {db.health_information_bundles.count_documents({})}")

    # Bundle breakdown
    for bundle_type in bundle_types:
        count = db.health_information_bundles.count_documents({"bundle_type": bundle_type})
        print(f"  - {bundle_type}: {count}")

    print("\n✅ Database seeding complete!")

    client.close()


def main():
    parser = argparse.ArgumentParser(description='Seed MongoDB with generated ABDM data')
    parser.add_argument('--mongo-uri', type=str,
                        default='mongodb://admin:abdm123@localhost:27017/abdm?authSource=admin',
                        help='MongoDB connection URI')
    parser.add_argument('--database', type=str, default='abdm', help='Database name')
    parser.add_argument('--data-dir', type=str, default='data/seed', help='Directory containing JSON data')
    parser.add_argument('--bundle-dir', type=str, default='data/seed/sample_bundles', help='Directory containing FHIR bundles')

    args = parser.parse_args()

    try:
        seed_database(args.mongo_uri, args.database, args.data_dir, args.bundle_dir)
    except Exception as e:
        print(f"\n❌ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
