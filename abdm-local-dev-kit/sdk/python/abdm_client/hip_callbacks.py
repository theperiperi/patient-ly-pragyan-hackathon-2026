"""
HIP Callbacks and Notifications Client

Provides helper methods for HIP (Health Information Provider) implementations:
1. Send notifications (add contexts, context notify)
2. Build properly formatted callback responses
3. Validate callback request/response schemas
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from .exceptions import ValidationError, ABDMError


class HIPCallbacksClient:
    """Client for HIP callback operations and notifications."""

    def __init__(self, parent_client):
        self.client = parent_client

    # ========================================================================
    # HIP-Initiated Requests (Notifications to Gateway)
    # ========================================================================

    async def add_care_contexts(
        self,
        patient_ref: str,
        link_ref: str,
        care_contexts: List[Dict[str, str]],
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Add new care contexts to an existing patient link.

        This allows HIPs to add new care contexts (episodes, visits) to a
        patient link without requiring new OTP verification.

        Args:
            patient_ref: Patient reference number at HIP
            link_ref: Existing link reference number
            care_contexts: List of care contexts to add
                [{"referenceNumber": "EP-003", "display": "New Visit"}]
            timeout: Request timeout in seconds

        Returns:
            {
                "acknowledged": true,
                "requestId": "uuid"
            }

        Raises:
            ValidationError: If invalid parameters
            ABDMError: If request fails

        Example:
            >>> await client.hip_callbacks.add_care_contexts(
            ...     patient_ref="PATIENT-001",
            ...     link_ref="LINK-ABC123",
            ...     care_contexts=[
            ...         {"referenceNumber": "EP-003", "display": "Cardiology Visit - 2024-02"},
            ...         {"referenceNumber": "EP-004", "display": "Lab Tests - 2024-02"}
            ...     ]
            ... )
        """
        if not patient_ref:
            raise ValidationError("patient_ref is required")

        if not link_ref:
            raise ValidationError("link_ref is required")

        if not care_contexts or len(care_contexts) == 0:
            raise ValidationError("At least one care context is required")

        # Validate care context structure
        for cc in care_contexts:
            if "referenceNumber" not in cc:
                raise ValidationError("Each care context must have 'referenceNumber'")

        # Build request
        request_id = str(uuid4())

        request_data = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "link": {
                "referenceNumber": link_ref,
                "display": f"Link {link_ref}",  # Required field
                "authenticationType": "DIRECT"
            },
            "patient": {
                "referenceNumber": patient_ref,
                "display": f"Patient {patient_ref}"  # Required field
            },
            "careContexts": care_contexts  # At root level, not under patient
        }

        # Send request
        response = await self.client.request(
            method="POST",
            endpoint="/v0.5/links/link/add-contexts",
            data=request_data
        )

        return {
            "acknowledged": response.get("acknowledgment", True),
            "requestId": request_id
        }

    async def notify_context(
        self,
        care_context: Dict[str, str],
        hi_types: List[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Notify HIU about a new available care context for a patient.

        This allows HIPs to proactively notify HIUs when new health records
        become available for a patient.

        Args:
            care_context: Single care context with patient and HIP info:
                {
                    "patientReference": "PATIENT-001",
                    "careContextReference": "EP-005",
                    "hiType": "DiagnosticReport"
                }
            hi_types: List of HI types (default: ["OPConsultation"])
            timeout: Request timeout in seconds

        Returns:
            {
                "acknowledged": true,
                "requestId": "uuid"
            }

        Raises:
            ValidationError: If invalid parameters
            ABDMError: If request fails

        Example:
            >>> await client.hip_callbacks.notify_context(
            ...     care_context={
            ...         "patientReference": "PATIENT-001",
            ...         "careContextReference": "EP-005",
            ...         "hiType": "DiagnosticReport"
            ...     },
            ...     hi_types=["DiagnosticReport", "Prescription"]
            ... )
        """
        if not care_context:
            raise ValidationError("care_context is required")

        if "patientReference" not in care_context:
            raise ValidationError("care_context must have 'patientReference'")

        if "careContextReference" not in care_context:
            raise ValidationError("care_context must have 'careContextReference'")

        # Default HI types
        if not hi_types:
            hi_types = care_context.get("hiType", "OPConsultation")
            if isinstance(hi_types, str):
                hi_types = [hi_types]

        # Build request
        request_id = str(uuid4())

        request_data = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "notification": {
                "careContext": {
                    "referenceNumber": care_context.get("careContextReference", care_context.get("referenceNumber", "UNKNOWN")),
                    "display": care_context.get("display", f"Care Context {care_context.get('careContextReference', 'UNKNOWN')}")
                },
                "hiTypes": hi_types,
                "date": datetime.now().isoformat() + "Z"
            }
        }

        # Send request
        response = await self.client.request(
            method="POST",
            endpoint="/v0.5/links/context/notify",
            data=request_data
        )

        return {
            "acknowledged": response.get("acknowledgment", True),
            "requestId": request_id
        }

    # ========================================================================
    # Callback Response Builders (For HIP Implementations)
    # ========================================================================

    @staticmethod
    def build_on_discover_response(
        request_id: str,
        transaction_id: str,
        patient: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a properly formatted response for on-discover callback.

        Args:
            request_id: Request ID from original discovery request
            transaction_id: Transaction ID from original request
            patient: Patient data if found:
                {
                    "referenceNumber": "PATIENT-001",
                    "display": "John Doe",
                    "careContexts": [
                        {"referenceNumber": "EP-001", "display": "OPD Visit"}
                    ],
                    "matchedBy": ["NDHM_HEALTH_NUMBER"]
                }
            error: Error details if patient not found:
                {"code": 1000, "message": "Patient not found"}

        Returns:
            Formatted callback response dictionary

        Example:
            >>> response = HIPCallbacksClient.build_on_discover_response(
            ...     request_id="req-123",
            ...     transaction_id="txn-456",
            ...     patient={
            ...         "referenceNumber": "PAT-001",
            ...         "display": "Jane Doe",
            ...         "careContexts": [{"referenceNumber": "EP-001", "display": "Visit"}],
            ...         "matchedBy": ["MOBILE"]
            ...     }
            ... )
        """
        response = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "transactionId": transaction_id,
            "resp": {
                "requestId": request_id
            }
        }

        if patient:
            response["patient"] = patient
        elif error:
            response["error"] = error

        return response

    @staticmethod
    def build_on_init_response(
        request_id: str,
        link: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a properly formatted response for on-init callback.

        Args:
            request_id: Request ID from original link init request
            link: Link reference if successful:
                {
                    "referenceNumber": "LINK-ABC123",
                    "authenticationType": "DIRECT",
                    "meta": {
                        "communicationMedium": "MOBILE",
                        "communicationHint": "+91******7890",
                        "communicationExpiry": "2024-02-14T10:30:00Z"
                    }
                }
            error: Error details if failed

        Returns:
            Formatted callback response dictionary
        """
        response = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "resp": {
                "requestId": request_id
            }
        }

        if link:
            response["link"] = link
        elif error:
            response["error"] = error

        return response

    @staticmethod
    def build_on_confirm_response(
        request_id: str,
        patient: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a properly formatted response for on-confirm callback.

        Args:
            request_id: Request ID from original confirm request
            patient: Linked patient data if successful:
                {
                    "referenceNumber": "PATIENT-001",
                    "display": "John Doe",
                    "careContexts": [
                        {"referenceNumber": "EP-001", "display": "Linked visit"}
                    ]
                }
            error: Error details if failed (e.g., invalid OTP)

        Returns:
            Formatted callback response dictionary
        """
        response = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "resp": {
                "requestId": request_id
            }
        }

        if patient:
            response["patient"] = patient
        elif error:
            response["error"] = error

        return response

    @staticmethod
    def build_on_request_response(
        request_id: str,
        hi_request: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a properly formatted response for on-request callback (health info).

        Args:
            request_id: Request ID from original HI request
            hi_request: Health information request acknowledgement:
                {
                    "transactionId": "txn-uuid",
                    "sessionStatus": "ACKNOWLEDGED"
                }
            error: Error details if failed

        Returns:
            Formatted callback response dictionary
        """
        response = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "resp": {
                "requestId": request_id
            }
        }

        if hi_request:
            response["hiRequest"] = hi_request
        elif error:
            response["error"] = error

        return response

    @staticmethod
    def build_on_add_contexts_response(
        request_id: str,
        acknowledgement: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a properly formatted response for on-add-contexts callback.

        Args:
            request_id: Request ID from original add contexts request
            acknowledgement: Acknowledgement if successful:
                {"status": "CONTEXTS_ADDED"}
            error: Error details if failed

        Returns:
            Formatted callback response dictionary
        """
        response = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "resp": {
                "requestId": request_id
            }
        }

        if acknowledgement:
            response["acknowledgement"] = acknowledgement
        elif error:
            response["error"] = error

        return response

    @staticmethod
    def build_on_notify_response(
        request_id: str,
        acknowledgement: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build a properly formatted response for on-notify callback.

        Args:
            request_id: Request ID from original context notify request
            acknowledgement: Acknowledgement if successful:
                {"status": "OK"}
            error: Error details if failed

        Returns:
            Formatted callback response dictionary
        """
        response = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "resp": {
                "requestId": request_id
            }
        }

        if acknowledgement:
            response["acknowledgement"] = acknowledgement
        elif error:
            response["error"] = error

        return response

    # ========================================================================
    # Validation Helpers
    # ========================================================================

    @staticmethod
    def validate_care_contexts(care_contexts: List[Dict[str, str]]) -> None:
        """
        Validate care contexts structure.

        Args:
            care_contexts: List of care contexts to validate

        Raises:
            ValidationError: If care contexts are invalid
        """
        if not isinstance(care_contexts, list):
            raise ValidationError("care_contexts must be a list")

        if len(care_contexts) == 0:
            raise ValidationError("At least one care context is required")

        for idx, cc in enumerate(care_contexts):
            if not isinstance(cc, dict):
                raise ValidationError(f"Care context #{idx} must be a dictionary")

            if "referenceNumber" not in cc:
                raise ValidationError(f"Care context #{idx} missing 'referenceNumber'")

            if "display" in cc and not isinstance(cc["display"], str):
                raise ValidationError(f"Care context #{idx} 'display' must be a string")

    @staticmethod
    def validate_patient_data(patient: Dict[str, Any]) -> None:
        """
        Validate patient data structure.

        Args:
            patient: Patient data to validate

        Raises:
            ValidationError: If patient data is invalid
        """
        required_fields = ["referenceNumber", "display"]

        for field in required_fields:
            if field not in patient:
                raise ValidationError(f"Patient data missing required field: {field}")

        if "careContexts" in patient:
            HIPCallbacksClient.validate_care_contexts(patient["careContexts"])
