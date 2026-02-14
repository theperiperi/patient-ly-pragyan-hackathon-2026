"""
Example 1: Patient Discovery

Demonstrates how to discover a patient by ABHA number or demographics.
"""

import asyncio
from abdm_client import ABDMClient, PatientNotFoundError


async def main():
    # Initialize client
    client = ABDMClient(
        base_url="http://localhost:8090",
        client_id="demo-hiu",
        client_secret="demo-secret",
        validate_schemas=True  # Enable automatic schema validation
    )

    print("=== Patient Discovery Examples ===\n")

    # Example 1: Discover by ABHA number
    print("1. Discovering patient by ABHA number...")
    try:
        result = await client.discover_patient(
            abha_number="22-7225-4829-5255"
        )

        patient = result["patient"]
        print(f"   ✓ Found: {patient['display']}")
        print(f"   Patient Ref: {patient['referenceNumber']}")
        print(f"   Care Contexts: {len(patient.get('careContexts', []))}")
        print(f"   Matched By: {', '.join(patient.get('matchedBy', []))}\n")

    except PatientNotFoundError as e:
        print(f"   ✗ Patient not found: {e}\n")

    # Example 2: Discover by mobile number
    print("2. Discovering patient by mobile number...")
    try:
        result = await client.discover_patient(
            mobile="+919876543210",
            name="John Doe",  # Optional, for fuzzy matching
            gender="M",
            year_of_birth=1990
        )

        patient = result["patient"]
        print(f"   ✓ Found: {patient['display']}")
        print(f"   Care Contexts:")
        for cc in patient.get('careContexts', []):
            print(f"     - {cc['referenceNumber']}: {cc['display']}")
        print()

    except PatientNotFoundError as e:
        print(f"   ✗ Patient not found: {e}\n")

    # Example 3: Discover by demographics (fuzzy matching)
    print("3. Discovering patient by name + demographics...")
    try:
        result = await client.discover_patient(
            name="Priya Sharma",
            gender="F",
            year_of_birth=1985
        )

        patient = result["patient"]
        print(f"   ✓ Found: {patient['display']}")
        print(f"   Matched By: Fuzzy demographics matching\n")

    except PatientNotFoundError as e:
        print(f"   ✗ Patient not found: {e}\n")

    # Example 4: Handle patient not found
    print("4. Handling patient not found...")
    try:
        result = await client.discover_patient(
            abha_number="99-9999-9999-9999"  # Non-existent
        )
    except PatientNotFoundError as e:
        print(f"   ✓ Correctly handled: {e}\n")

    # Close client
    await client.close()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
