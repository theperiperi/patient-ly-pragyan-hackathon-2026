"""
Care Context Linking Client

Handles OTP-based care context linking.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from .exceptions import LinkingError, ValidationError


class LinkingClient:
    """Client for care context linking operations."""

    def __init__(self, parent_client):
        self.client = parent_client

    async def initiate(
        self,
        patient_ref: str,
        care_contexts: List[str],
        patient_abha: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Initiate care context linking (generates OTP).

        Args:
            patient_ref: Patient reference at HIP (e.g., "PATIENT-001")
            care_contexts: List of care context IDs (e.g., ["EP-001", "EP-002"])
            patient_abha: Patient ABHA with @sbx
            timeout: Callback timeout in seconds

        Returns:
            {
                "linkRefNumber": "LINK-ABC123",
                "authenticationType": "DIRECT",
                "meta": {
                    "communicationMedium": "MOBILE",
                    "communicationHint": "+91******7890",
                    "communicationExpiry": "2024-01-15T10:30:00Z"
                }
            }

        Raises:
            ValidationError: If invalid parameters
            LinkingError: If linking fails
        """
        if not patient_ref:
            raise ValidationError("patient_ref is required")

        if not care_contexts or len(care_contexts) == 0:
            raise ValidationError("At least one care context is required")

        # Build request
        request_id = str(uuid4())
        transaction_id = str(uuid4())

        request_data = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat(),
            "transactionId": transaction_id,
            "patient": {
                "id": patient_abha or f"{patient_ref}@sbx",
                "referenceNumber": patient_ref,
                "careContexts": [
                    {"referenceNumber": cc} for cc in care_contexts
                ]
            }
        }

        # Send link init request
        response = await self.client.request(
            method="POST",
            endpoint="/v0.5/links/link/init",
            data=request_data,
            validate_response_schema="PatientLinkReferenceResult"
        )

        # Check for errors
        if "error" in response:
            raise LinkingError(
                response["error"].get("message", "Linking failed"),
                error_code=response["error"].get("code"),
                details=response["error"]
            )

        if not response.get("link"):
            raise LinkingError("No link reference returned")

        return {
            "linkRefNumber": response["link"]["referenceNumber"],
            "authenticationType": response["link"]["authenticationType"],
            "meta": response["link"].get("meta", {}),
            "transactionId": transaction_id
        }

    async def confirm(
        self,
        link_ref: str,
        otp: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Confirm care context linking with OTP.

        Args:
            link_ref: Link reference from initiate()
            otp: OTP received by patient
            timeout: Callback timeout in seconds

        Returns:
            {
                "patient": {
                    "referenceNumber": "PATIENT-001",
                    "display": "John Doe",
                    "careContexts": [
                        {"referenceNumber": "EP-001", "display": "OPD Visit"}
                    ]
                }
            }

        Raises:
            LinkingError: If OTP is invalid or linking fails
        """
        if not link_ref:
            raise ValidationError("link_ref is required")

        if not otp:
            raise ValidationError("OTP is required")

        # Build request
        request_id = str(uuid4())

        request_data = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat(),
            "confirmation": {
                "linkRefNumber": link_ref,
                "token": otp
            }
        }

        # Send confirm request
        response = await self.client.request(
            method="POST",
            endpoint="/v0.5/links/link/confirm",
            data=request_data,
            validate_response_schema="PatientLinkResult"
        )

        # Check for errors
        if "error" in response:
            error_msg = response["error"].get("message", "Invalid OTP or linking failed")
            raise LinkingError(
                error_msg,
                error_code=response["error"].get("code"),
                details=response["error"]
            )

        if not response.get("patient"):
            raise LinkingError("Link confirmation failed")

        return {
            "patient": response["patient"]
        }
