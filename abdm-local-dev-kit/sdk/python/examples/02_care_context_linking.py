"""
Example 2: Care Context Linking

Demonstrates OTP-based care context linking.
"""

import asyncio
from abdm_client import ABDMClient, LinkingError


async def main():
    client = ABDMClient(
        base_url="http://localhost:8090",
        validate_schemas=True
    )

    print("=== Care Context Linking Example ===\n")

    # Step 1: Discover patient first
    print("Step 1: Discovering patient...")
    discovery_result = await client.discover_patient(
        abha_number="22-7225-4829-5255"
    )

    patient = discovery_result["patient"]
    patient_ref = patient["referenceNumber"]
    care_contexts = [cc["referenceNumber"] for cc in patient.get("careContexts", [])]

    print(f"   Found patient: {patient['display']}")
    print(f"   Patient Ref: {patient_ref}")
    print(f"   Available care contexts: {len(care_contexts)}\n")

    if not care_contexts:
        print("No care contexts available to link. Exiting.")
        await client.close()
        return

    # Step 2: Initiate linking (generates OTP)
    print("Step 2: Initiating care context linking...")
    link_result = await client.initiate_linking(
        patient_ref=patient_ref,
        care_contexts=care_contexts[:2]  # Link first 2 care contexts
    )

    link_ref = link_result["linkRefNumber"]
    print(f"   ✓ Link initiated!")
    print(f"   Link Ref: {link_ref}")
    print(f"   Auth Type: {link_result['authenticationType']}")

    if "meta" in link_result and link_result["meta"]:
        meta = link_result["meta"]
        print(f"   OTP sent via: {meta.get('communicationMedium', 'N/A')}")
        print(f"   Hint: {meta.get('communicationHint', 'N/A')}")
        print(f"   Expires: {meta.get('communicationExpiry', 'N/A')}")

    # In production, patient receives OTP on their phone
    # For this demo, check HIP logs for the OTP
    print("\n   🔐 Check HIP service logs for the OTP")
    print("   (In production, patient receives it via SMS)\n")

    # Step 3: Simulate OTP entry
    print("Step 3: Enter the OTP to confirm linking")
    otp = input("   Enter OTP (from HIP logs): ").strip()

    if not otp:
        print("   No OTP entered. Skipping confirmation.")
        await client.close()
        return

    # Step 4: Confirm linking with OTP
    print("\nStep 4: Confirming with OTP...")
    try:
        confirm_result = await client.confirm_linking(
            link_ref=link_ref,
            otp=otp
        )

        linked_patient = confirm_result["patient"]
        print(f"   ✓ Successfully linked!")
        print(f"   Patient: {linked_patient['display']}")
        print(f"   Linked care contexts: {len(linked_patient.get('careContexts', []))}")

        for cc in linked_patient.get("careContexts", []):
            print(f"     - {cc['referenceNumber']}: {cc['display']}")

    except LinkingError as e:
        print(f"   ✗ Linking failed: {e}")
        print(f"   Error code: {e.error_code}")

    await client.close()
    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
