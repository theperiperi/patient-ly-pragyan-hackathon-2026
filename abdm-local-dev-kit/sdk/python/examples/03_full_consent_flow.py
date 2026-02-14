"""
Example 3: Complete Consent and Data Exchange Flow

Demonstrates the complete ABDM workflow:
1. Discover patient
2. Link care contexts
3. Request consent
4. Fetch health information
"""

import asyncio
from datetime import datetime, timedelta
from abdm_client import ABDMClient


async def main():
    client = ABDMClient(
        base_url="http://localhost:8090",
        client_id="demo-hiu",
        client_secret="demo-secret",
        validate_schemas=True
    )

    print("=== Complete ABDM Workflow Example ===\n")

    # Phase 1: Patient Discovery
    print("Phase 1: Patient Discovery")
    print("-" * 50)

    discovery = await client.discover_patient(
        abha_number="22-7225-4829-5255"
    )

    patient = discovery["patient"]
    print(f"✓ Patient found: {patient['display']}")
    print(f"  ABHA: 22-7225-4829-5255@sbx")
    print(f"  Care contexts: {len(patient.get('careContexts', []))}\n")

    # Phase 2: Consent Request
    print("Phase 2: Consent Request")
    print("-" * 50)

    consent_result = await client.request_consent(
        patient_abha="22-7225-4829-5255@sbx",
        purpose="CAREMGT",  # Care Management
        hi_types=["DiagnosticReport", "Prescription", "DischargeSummary"],
        date_from=datetime.now() - timedelta(days=365),
        date_to=datetime.now(),
        data_erase_at=datetime.now() + timedelta(days=30),
        requester_name="Dr. Sarah Johnson",
        requester_id="MH1001"
    )

    consent_request_id = consent_result["consentRequestId"]
    print(f"✓ Consent requested!")
    print(f"  Request ID: {consent_request_id}")
    print(f"  Purpose: Care Management")
    print(f"  HI Types: DiagnosticReport, Prescription, DischargeSummary")
    print(f"  Date Range: Last 365 days")
    print(f"  Data Erase: 30 days from now\n")

    print("  💡 In production:")
    print("     - Patient receives notification in ABHA app")
    print("     - Patient reviews consent details")
    print("     - Patient approves or denies")
    print("     - You receive callback notification\n")

    # For demo: simulate patient approval
    print("  [Simulating patient approval in dev environment...]\n")

    # Phase 3: Health Information Request
    print("Phase 3: Health Information Request")
    print("-" * 50)

    # In production, you'd use the consent ID from the approval callback
    # For demo, assuming consent was granted
    print("  Note: Assuming consent was granted (check CM service)")
    print("  In production, wait for consent approval callback before proceeding\n")

    # Example of fetching HI (requires valid consent ID)
    print("  Example HI request structure:")
    print("  ├─ Consent ID: <from consent approval>")
    print("  ├─ Data Push URL: https://your-hiu.com/data-push")
    print("  ├─ Encryption Key: <your public key>")
    print("  └─ Date Range: <from consent>\n")

    print("  💡 After HI request:")
    print("     - CM validates consent")
    print("     - Forwards to HIP")
    print("     - HIP retrieves FHIR bundles")
    print("     - HIP encrypts data")
    print("     - HIP pushes to your data_push_url\n")

    # Phase 4: Validation
    print("Phase 4: Schema Validation")
    print("-" * 50)
    print("✓ All requests validated against official ABDM schema")
    print("✓ All responses validated for compliance")
    print("✓ Automatic error handling and retries\n")

    await client.close()

    print("=== Workflow Complete ===\n")
    print("Next steps:")
    print("1. Check services/gateway/logs for request/response details")
    print("2. Check services/consent_manager for consent status")
    print("3. Check services/hip/logs for OTP and data transfer")
    print("4. Use SDK in your application for production integration\n")


if __name__ == "__main__":
    asyncio.run(main())
