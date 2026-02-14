"""
Consent Management Client

Handles consent request and artefact operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4

from .exceptions import ConsentError, ValidationError

# Valid ABDM purpose codes
VALID_PURPOSE_CODES = {
    "CAREMGT",  # Care Management
    "BTG",      # Break the Glass
    "PUBHLTH",  # Public Health
    "HPAYMT",   # Healthcare Payment
    "DSRCH",    # Disease Specific Healthcare Research
    "PATRQT"    # Self Requested
}

# Valid HI types
VALID_HI_TYPES = {
    "OPConsultation",
    "Prescription",
    "DischargeSummary",
    "DiagnosticReport",
    "ImmunizationRecord",
    "HealthDocumentRecord",
    "WellnessRecord"
}


class ConsentClient:
    """Client for consent management operations."""

    def __init__(self, parent_client):
        self.client = parent_client

    async def request(
        self,
        patient_abha: str,
        purpose: str,
        hi_types: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        data_erase_at: Optional[datetime] = None,
        requester_name: str = "Dr. John Doe",
        requester_id: str = "MH1001",
        requester_system: str = "https://www.mciindia.org",
        access_mode: str = "VIEW",
        frequency_unit: str = "DAY",
        frequency_value: int = 1,
        frequency_repeats: int = 1,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Request patient consent for health information access.

        Args:
            patient_abha: Patient ABHA with @sbx (e.g., "22-7225-4829-5255@sbx")
            purpose: Purpose code (CAREMGT, BTG, PUBHLTH, HPAYMT, DSRCH, PATRQT)
            hi_types: List of HI types to access
            date_from: Data from date (default: 1 year ago)
            date_to: Data to date (default: today)
            data_erase_at: When to erase data (default: 30 days from now)
            requester_name: Requester name
            requester_id: Requester registration ID
            requester_system: Identifier system URL
            access_mode: VIEW, STORE, QUERY, or STREAM
            frequency_unit: HOUR, DAY, WEEK, MONTH, YEAR
            frequency_value: Frequency value
            frequency_repeats: Number of repeats
            timeout: Callback timeout

        Returns:
            {
                "consentRequestId": "uuid",
                "requestId": "uuid",
                "timestamp": "2024-01-15T10:00:00Z"
            }

        Raises:
            ValidationError: If invalid parameters
            ConsentError: If consent request fails
        """
        # Validate purpose code
        if purpose not in VALID_PURPOSE_CODES:
            raise ValidationError(
                f"Invalid purpose code: {purpose}. Must be one of: {', '.join(VALID_PURPOSE_CODES)}"
            )

        # Validate HI types
        invalid_types = [t for t in hi_types if t not in VALID_HI_TYPES]
        if invalid_types:
            raise ValidationError(
                f"Invalid HI types: {', '.join(invalid_types)}. "
                f"Valid types: {', '.join(VALID_HI_TYPES)}"
            )

        # Validate patient ABHA format
        if "@" not in patient_abha:
            patient_abha = f"{patient_abha}@sbx"

        # Set defaults
        if date_from is None:
            date_from = datetime.now() - timedelta(days=365)
        if date_to is None:
            date_to = datetime.now()
        if data_erase_at is None:
            data_erase_at = datetime.now() + timedelta(days=30)

        # Build request
        request_id = str(uuid4())

        request_data = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat(),
            "consent": {
                "purpose": {
                    "text": self._get_purpose_text(purpose),
                    "code": purpose,
                    "refUri": "http://terminology.hl7.org/ValueSet/v3-PurposeOfUse"
                },
                "patient": {
                    "id": patient_abha
                },
                "hiu": {
                    "id": self.client.client_id or "HIU-001"
                },
                "requester": {
                    "name": requester_name,
                    "identifier": {
                        "type": "REGNO",
                        "value": requester_id,
                        "system": requester_system
                    }
                },
                "hiTypes": hi_types,
                "permission": {
                    "accessMode": access_mode,
                    "dateRange": {
                        "from": date_from.isoformat(),
                        "to": date_to.isoformat()
                    },
                    "dataEraseAt": data_erase_at.isoformat(),
                    "frequency": {
                        "unit": frequency_unit,
                        "value": frequency_value,
                        "repeats": frequency_repeats
                    }
                },
                "consentNotificationUrl": f"{self.client.base_url}/callback/consent"
            }
        }

        # Send consent request
        response = await self.client.request(
            method="POST",
            endpoint="/v0.5/consent-requests/init",
            data=request_data
        )

        # Check for errors
        if "error" in response:
            raise ConsentError(
                response["error"].get("message", "Consent request failed"),
                error_code=response["error"].get("code"),
                details=response["error"]
            )

        return {
            "consentRequestId": response.get("consentRequest", {}).get("id"),
            "requestId": request_id,
            "timestamp": response.get("timestamp")
        }

    def _get_purpose_text(self, purpose_code: str) -> str:
        """Get human-readable text for purpose code."""
        purpose_map = {
            "CAREMGT": "Care Management",
            "BTG": "Break the Glass",
            "PUBHLTH": "Public Health",
            "HPAYMT": "Healthcare Payment",
            "DSRCH": "Disease Specific Healthcare Research",
            "PATRQT": "Self Requested"
        }
        return purpose_map.get(purpose_code, purpose_code)

    async def fetch(
        self,
        consent_id: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Fetch consent artefact by ID.

        Args:
            consent_id: Consent artefact ID
            timeout: Callback timeout

        Returns:
            Consent artefact details

        Raises:
            ConsentError: If consent fetch fails
        """
        request_id = str(uuid4())

        request_data = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat(),
            "consentId": consent_id
        }

        response = await self.client.request(
            method="POST",
            endpoint="/v0.5/consents/fetch",
            data=request_data
        )

        if "error" in response:
            raise ConsentError(
                response["error"].get("message", "Consent fetch failed"),
                error_code=response["error"].get("code")
            )

        return response.get("consent", {})
