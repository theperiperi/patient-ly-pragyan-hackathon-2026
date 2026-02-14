"""
Health Information Request Client

Handles health information requests and data transfer.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import uuid4
import base64
import os

from .exceptions import ConsentError, ValidationError


class HealthInformationClient:
    """Client for health information request operations."""

    def __init__(self, parent_client):
        self.client = parent_client

    async def request(
        self,
        consent_id: str,
        data_push_url: str,
        encryption_public_key: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Request health information after consent granted.

        Args:
            consent_id: Consent artefact ID
            data_push_url: URL where HIP should push encrypted data
            encryption_public_key: Public key for encryption (base64). If None, generates one
            date_from: Data from date (default: from consent)
            date_to: Data to date (default: from consent)
            timeout: Callback timeout

        Returns:
            {
                "transactionId": "uuid",
                "sessionStatus": "REQUESTED"
            }

        Raises:
            ConsentError: If consent is invalid
            ValidationError: If invalid parameters
        """
        if not consent_id:
            raise ValidationError("consent_id is required")

        if not data_push_url:
            raise ValidationError("data_push_url is required")

        # Generate encryption key if not provided (for demo purposes)
        if not encryption_public_key:
            encryption_public_key = self._generate_demo_key()

        # Set date defaults
        if date_from is None:
            date_from = datetime.now() - timedelta(days=365)
        if date_to is None:
            date_to = datetime.now()

        # Build request
        request_id = str(uuid4())

        request_data = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat(),
            "hiRequest": {
                "consent": {
                    "id": consent_id
                },
                "dateRange": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                },
                "dataPushUrl": data_push_url,
                "keyMaterial": {
                    "cryptoAlg": "ECDH",
                    "curve": "Curve25519",
                    "dhPublicKey": {
                        "expiry": (datetime.now() + timedelta(days=1)).isoformat(),
                        "parameters": "Curve25519/32byte random key",
                        "keyValue": encryption_public_key
                    },
                    "nonce": self._generate_nonce()
                }
            }
        }

        # Send HI request
        response = await self.client.request(
            method="POST",
            endpoint="/v0.5/health-information/cm/request",
            data=request_data,
            validate_response_schema="HIUHealthInformationRequestResponse"
        )

        # Check for errors
        if "error" in response:
            raise ConsentError(
                response["error"].get("message", "Health information request failed"),
                error_code=response["error"].get("code"),
                details=response["error"]
            )

        hi_request = response.get("hiRequest", {})

        return {
            "transactionId": hi_request.get("transactionId"),
            "sessionStatus": hi_request.get("sessionStatus"),
            "requestId": request_id
        }

    def _generate_demo_key(self) -> str:
        """Generate a demo public key (base64 encoded random bytes)."""
        random_bytes = os.urandom(32)
        return base64.b64encode(random_bytes).decode('utf-8')

    def _generate_nonce(self) -> str:
        """Generate a random nonce."""
        return str(uuid4())
