"""
Test SDK HIP Callbacks Against Live HIP Service

Tests the new SDK HIP callback methods against the running HIP service.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from jose import jwt

# Add SDK to path
sdk_path = Path(__file__).parent.parent / "sdk" / "python"
sys.path.insert(0, str(sdk_path))

from abdm_client import ABDMClient


def generate_jwt_token() -> str:
    """Generate a valid JWT token for testing."""
    payload = {
        "sub": "test-sdk-client",
        "exp": datetime.now() + timedelta(hours=1),
        "iat": datetime.now()
    }
    secret = "abdm-local-dev-secret-key-change-in-production"
    algorithm = "HS256"
    return jwt.encode(payload, secret, algorithm=algorithm)


async def test_add_care_contexts():
    """Test adding care contexts to an existing link."""
    print("\n" + "="*80)
    print("TEST: Add Care Contexts")
    print("="*80)

    async with ABDMClient(
        base_url="http://localhost:8092",
        validate_schemas=False
    ) as client:
        # Add JWT token to client headers
        token = generate_jwt_token()
        client.http_client.headers["Authorization"] = f"Bearer {token}"

        try:
            result = await client.hip_callbacks.add_care_contexts(
                patient_ref="PATIENT-001",
                link_ref="LINK-ABC123",
                care_contexts=[
                    {
                        "referenceNumber": "EP-TEST-001",
                        "display": "SDK Test Visit - 2024-02-14"
                    }
                ]
            )

            print(f"✅ PASSED - Add Care Contexts")
            print(f"   Request ID: {result['requestId']}")
            print(f"   Acknowledged: {result.get('acknowledged', True)}")
            return True

        except Exception as e:
            print(f"❌ FAILED - Add Care Contexts")
            print(f"   Error: {str(e)}")
            return False


async def test_notify_context():
    """Test notifying HIU about new care contexts."""
    print("\n" + "="*80)
    print("TEST: Notify Context")
    print("="*80)

    async with ABDMClient(
        base_url="http://localhost:8092",
        validate_schemas=False
    ) as client:
        # Add JWT token to client headers
        token = generate_jwt_token()
        client.http_client.headers["Authorization"] = f"Bearer {token}"

        try:
            result = await client.hip_callbacks.notify_context(
                care_context={
                    "patientReference": "PATIENT-001",
                    "careContextReference": "NOTIFY-TEST-001",
                    "hiType": "DiagnosticReport"
                },
                hi_types=["DiagnosticReport"]
            )

            print(f"✅ PASSED - Notify Context")
            print(f"   Request ID: {result['requestId']}")
            print(f"   Acknowledged: {result.get('acknowledged', True)}")
            return True

        except Exception as e:
            print(f"❌ FAILED - Notify Context")
            print(f"   Error: {str(e)}")
            return False


async def main():
    """Run all SDK HIP callback tests."""
    print("\n" + "="*80)
    print("SDK HIP CALLBACKS - INTEGRATION TESTS")
    print("="*80)
    print("\nTesting new SDK methods against running HIP service...")

    results = []

    # Test add_care_contexts
    results.append(await test_add_care_contexts())

    # Test notify_context
    results.append(await test_notify_context())

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ ALL SDK HIP CALLBACK TESTS PASSED")
    else:
        print(f"❌ {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
