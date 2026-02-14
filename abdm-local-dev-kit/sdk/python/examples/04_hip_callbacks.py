"""
Example: HIP Callback Operations

Demonstrates how HIPs can use the SDK to:
1. Add new care contexts to existing patient links
2. Notify HIUs about new available health records
3. Build properly formatted callback responses

This example is for HIP (Health Information Provider) implementations.
"""

import asyncio
from abdm_client import ABDMClient, HIPCallbacksClient


async def example_add_care_contexts():
    """Example: Add new care contexts to an existing patient link."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Add Care Contexts to Existing Link")
    print("="*80)

    async with ABDMClient(
        base_url="http://localhost:8092",  # HIP service URL
        validate_schemas=False  # Disable for demo
    ) as client:
        try:
            # Scenario: Patient has an existing link, and HIP wants to add
            # new care contexts (new visits, lab results) to that link
            result = await client.hip_callbacks.add_care_contexts(
                patient_ref="PATIENT-001",
                link_ref="LINK-ABC123",
                care_contexts=[
                    {
                        "referenceNumber": "EP-003",
                        "display": "Cardiology Follow-up - 2024-02-14"
                    },
                    {
                        "referenceNumber": "LAB-456",
                        "display": "Blood Test Results - 2024-02-14"
                    }
                ]
            )

            print(f"✅ Successfully added care contexts")
            print(f"   Request ID: {result['requestId']}")
            print(f"   Acknowledged: {result['acknowledged']}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")


async def example_notify_context():
    """Example: Notify HIU about new available care contexts."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Notify HIU About New Health Records")
    print("="*80)

    async with ABDMClient(
        base_url="http://localhost:8092",  # HIP service URL
        validate_schemas=False
    ) as client:
        try:
            # Scenario: Patient gets a new discharge summary, HIP proactively
            # notifies HIU that new health record is available
            result = await client.hip_callbacks.notify_context(
                patient_abha="22-7225-4829-5255@sbx",
                hip_id="Apollo-Hospitals-Bangalore",
                care_contexts=[
                    {
                        "referenceNumber": "DISCHARGE-789",
                        "display": "Discharge Summary - Cardiac Surgery - 2024-02-14"
                    }
                ]
            )

            print(f"✅ Successfully notified HIU")
            print(f"   Request ID: {result['requestId']}")
            print(f"   Acknowledged: {result['acknowledged']}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")


def example_build_callback_responses():
    """Example: Build properly formatted callback responses."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Build Callback Responses (For HIP Implementations)")
    print("="*80)

    # Example 1: on-discover callback (patient found)
    print("\n--- on-discover Response (Patient Found) ---")
    on_discover_response = HIPCallbacksClient.build_on_discover_response(
        request_id="req-123",
        transaction_id="txn-456",
        patient={
            "referenceNumber": "PATIENT-001",
            "display": "Jane Doe",
            "careContexts": [
                {"referenceNumber": "EP-001", "display": "OPD Visit - 2024-01-15"},
                {"referenceNumber": "EP-002", "display": "Lab Tests - 2024-01-20"}
            ],
            "matchedBy": ["MOBILE"]
        }
    )
    print(f"✅ Response structure:")
    print(f"   Request ID: {on_discover_response['requestId']}")
    print(f"   Patient: {on_discover_response['patient']['display']}")
    print(f"   Care Contexts: {len(on_discover_response['patient']['careContexts'])}")

    # Example 2: on-discover callback (patient not found)
    print("\n--- on-discover Response (Patient Not Found) ---")
    on_discover_error = HIPCallbacksClient.build_on_discover_response(
        request_id="req-789",
        transaction_id="txn-012",
        error={"code": 1000, "message": "Patient not found"}
    )
    print(f"✅ Error response structure:")
    print(f"   Request ID: {on_discover_error['requestId']}")
    print(f"   Error Code: {on_discover_error['error']['code']}")
    print(f"   Error Message: {on_discover_error['error']['message']}")

    # Example 3: on-init callback (OTP sent)
    print("\n--- on-init Response (Link Initialized, OTP Sent) ---")
    on_init_response = HIPCallbacksClient.build_on_init_response(
        request_id="req-456",
        link={
            "referenceNumber": "LINK-XYZ789",
            "authenticationType": "DIRECT",
            "meta": {
                "communicationMedium": "MOBILE",
                "communicationHint": "+91******7890",
                "communicationExpiry": "2024-02-14T12:30:00Z"
            }
        }
    )
    print(f"✅ Response structure:")
    print(f"   Link Reference: {on_init_response['link']['referenceNumber']}")
    print(f"   OTP Sent To: {on_init_response['link']['meta']['communicationHint']}")
    print(f"   Expires At: {on_init_response['link']['meta']['communicationExpiry']}")

    # Example 4: on-confirm callback (link confirmed)
    print("\n--- on-confirm Response (Link Confirmed with OTP) ---")
    on_confirm_response = HIPCallbacksClient.build_on_confirm_response(
        request_id="req-789",
        patient={
            "referenceNumber": "PATIENT-001",
            "display": "John Doe",
            "careContexts": [
                {"referenceNumber": "EP-001", "display": "Linked OPD Visit"}
            ]
        }
    )
    print(f"✅ Response structure:")
    print(f"   Patient: {on_confirm_response['patient']['display']}")
    print(f"   Linked Contexts: {len(on_confirm_response['patient']['careContexts'])}")

    # Example 5: on-request callback (health info request acknowledged)
    print("\n--- on-request Response (HI Request Acknowledged) ---")
    on_request_response = HIPCallbacksClient.build_on_request_response(
        request_id="req-012",
        hi_request={
            "transactionId": "txn-abc-def",
            "sessionStatus": "ACKNOWLEDGED"
        }
    )
    print(f"✅ Response structure:")
    print(f"   Transaction ID: {on_request_response['hiRequest']['transactionId']}")
    print(f"   Session Status: {on_request_response['hiRequest']['sessionStatus']}")

    # Example 6: on-add-contexts callback
    print("\n--- on-add-contexts Response (Contexts Added) ---")
    on_add_contexts_response = HIPCallbacksClient.build_on_add_contexts_response(
        request_id="req-345",
        acknowledgement={"status": "CONTEXTS_ADDED"}
    )
    print(f"✅ Response structure:")
    print(f"   Status: {on_add_contexts_response['acknowledgement']['status']}")

    # Example 7: on-notify callback
    print("\n--- on-notify Response (Notification Acknowledged) ---")
    on_notify_response = HIPCallbacksClient.build_on_notify_response(
        request_id="req-678",
        acknowledgement={"status": "OK"}
    )
    print(f"✅ Response structure:")
    print(f"   Status: {on_notify_response['acknowledgement']['status']}")


def example_validation_helpers():
    """Example: Use validation helpers."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Validation Helpers")
    print("="*80)

    # Valid care contexts
    print("\n--- Valid Care Contexts ---")
    valid_care_contexts = [
        {"referenceNumber": "EP-001", "display": "Visit 1"},
        {"referenceNumber": "EP-002", "display": "Visit 2"}
    ]
    try:
        HIPCallbacksClient.validate_care_contexts(valid_care_contexts)
        print("✅ Care contexts are valid")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Invalid care contexts (missing referenceNumber)
    print("\n--- Invalid Care Contexts (Missing referenceNumber) ---")
    invalid_care_contexts = [
        {"display": "Visit 1"}  # Missing referenceNumber
    ]
    try:
        HIPCallbacksClient.validate_care_contexts(invalid_care_contexts)
        print("✅ Care contexts are valid")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Valid patient data
    print("\n--- Valid Patient Data ---")
    valid_patient = {
        "referenceNumber": "PATIENT-001",
        "display": "Jane Doe",
        "careContexts": [
            {"referenceNumber": "EP-001", "display": "Visit"}
        ]
    }
    try:
        HIPCallbacksClient.validate_patient_data(valid_patient)
        print("✅ Patient data is valid")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

    # Invalid patient data (missing required field)
    print("\n--- Invalid Patient Data (Missing display) ---")
    invalid_patient = {
        "referenceNumber": "PATIENT-001"
        # Missing 'display' field
    }
    try:
        HIPCallbacksClient.validate_patient_data(invalid_patient)
        print("✅ Patient data is valid")
    except Exception as e:
        print(f"❌ Validation failed: {e}")


async def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("HIP CALLBACKS AND NOTIFICATIONS - SDK EXAMPLES")
    print("="*80)
    print("\nThese examples demonstrate how HIPs can use the SDK to:")
    print("  1. Add new care contexts to existing patient links")
    print("  2. Notify HIUs about new available health records")
    print("  3. Build properly formatted callback responses")
    print("  4. Validate request/response data structures")

    # Note: Examples 1 and 2 require a running HIP service
    # Uncomment to test against a live service:
    # await example_add_care_contexts()
    # await example_notify_context()

    # Examples 3 and 4 are pure utility functions (no service required)
    example_build_callback_responses()
    example_validation_helpers()

    print("\n" + "="*80)
    print("✅ All examples completed!")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Start the HIP service: docker-compose up hip")
    print("  2. Uncomment examples 1 and 2 in this script")
    print("  3. Run: python examples/04_hip_callbacks.py")
    print("\nFor HIP implementations:")
    print("  - Use add_care_contexts() to add new episodes to existing links")
    print("  - Use notify_context() to proactively alert HIUs about new records")
    print("  - Use build_*_response() helpers in your FastAPI callback endpoints")


if __name__ == "__main__":
    asyncio.run(main())
