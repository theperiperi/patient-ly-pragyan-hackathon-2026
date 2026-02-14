"""
Patient Discovery Client

Handles patient discovery by ABHA number, mobile, or demographics.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import uuid4

from .exceptions import PatientNotFoundError, ValidationError


class DiscoveryClient:
    """Client for patient discovery operations."""

    def __init__(self, parent_client):
        self.client = parent_client

    async def discover(
        self,
        abha_number: Optional[str] = None,
        mobile: Optional[str] = None,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        year_of_birth: Optional[int] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Discover patient by identifiers or demographics.

        At minimum, must provide either:
        - ABHA number, OR
        - Mobile number, OR
        - Name + Gender + Year of Birth

        Args:
            abha_number: Patient ABHA (e.g., "22-7225-4829-5255")
            mobile: Mobile number (e.g., "+919876543210")
            name: Patient name
            gender: M, F, O, or U
            year_of_birth: Birth year (e.g., 1990)
            timeout: Callback timeout in seconds

        Returns:
            {
                "patient": {
                    "referenceNumber": "PATIENT-001",
                    "display": "John Doe",
                    "careContexts": [
                        {"referenceNumber": "EP-001", "display": "OPD Visit 2024-01"}
                    ],
                    "matchedBy": ["NDHM_HEALTH_NUMBER"]
                },
                "transactionId": "uuid"
            }

        Raises:
            ValidationError: If invalid parameters
            PatientNotFoundError: If no patient found
        """
        # Validate inputs
        if not any([abha_number, mobile, (name and gender and year_of_birth)]):
            raise ValidationError(
                "Must provide either ABHA number, mobile, or (name + gender + year_of_birth)"
            )

        if gender and gender not in ["M", "F", "O", "U"]:
            raise ValidationError(f"Invalid gender: {gender}. Must be M, F, O, or U")

        # Build verified identifiers
        verified_identifiers = []

        if abha_number:
            verified_identifiers.append({
                "type": "NDHM_HEALTH_NUMBER",
                "value": abha_number
            })

        if mobile:
            verified_identifiers.append({
                "type": "MOBILE",
                "value": mobile
            })

        # Build request
        request_id = str(uuid4())
        transaction_id = str(uuid4())

        request_data = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat(),
            "transactionId": transaction_id,
            "patient": {
                "id": f"{abha_number or 'unknown'}@sbx",
                "verifiedIdentifiers": verified_identifiers,
                "name": name or "Unknown",
                "gender": gender or "U",
                "yearOfBirth": year_of_birth or 2000
            }
        }

        # Send discovery request
        response = await self.client.request(
            method="POST",
            endpoint="/v0.5/care-contexts/discover",
            data=request_data,
            validate_response_schema="PatientDiscoveryResult"
        )

        # Check for patient in response
        if "error" in response:
            raise PatientNotFoundError(
                response["error"].get("message", "Patient not found"),
                error_code=response["error"].get("code"),
                details=response["error"]
            )

        if not response.get("patient"):
            raise PatientNotFoundError("No patient found matching criteria")

        return {
            "patient": response["patient"],
            "transactionId": transaction_id,
            "requestId": request_id
        }
