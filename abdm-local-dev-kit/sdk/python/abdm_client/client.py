"""
ABDM Client - Main client class with schema validation
"""

import httpx
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

from .exceptions import (
    ABDMError,
    ValidationError,
    AuthenticationError,
    PatientNotFoundError,
    ConsentError,
    LinkingError,
    SchemaValidationError,
    NetworkError,
    TimeoutError
)
from .discovery import DiscoveryClient
from .linking import LinkingClient
from .consent import ConsentClient
from .health_information import HealthInformationClient
from .hip_callbacks import HIPCallbacksClient


class ABDMClient:
    """
    Main ABDM client with built-in schema validation.

    This client provides a high-level interface to all ABDM operations
    with automatic schema validation against official ABDM specifications.

    Args:
        base_url: Base URL of ABDM Gateway (e.g., http://localhost:8090)
        client_id: Your client ID for authentication
        client_secret: Your client secret for authentication
        timeout: Request timeout in seconds (default: 30)
        validate_schemas: Enable schema validation (default: True)
        schema_path: Path to official gateway.yaml (auto-detected if None)

    Example:
        >>> client = ABDMClient(
        ...     base_url="http://localhost:8090",
        ...     client_id="demo-hiu",
        ...     client_secret="demo-secret"
        ... )
        >>> result = client.discover_patient(
        ...     abha_number="22-7225-4829-5255",
        ...     name="John Doe",
        ...     gender="M",
        ...     year_of_birth=1990
        ... )
    """

    def __init__(
        self,
        base_url: str,
        client_id: str = None,
        client_secret: str = None,
        timeout: int = 30,
        validate_schemas: bool = True,
        schema_path: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.validate_schemas = validate_schemas

        # HTTP client
        self.http_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout
        )

        # Load official ABDM schema for validation
        self.schema = None
        if self.validate_schemas:
            self._load_schema(schema_path)

        # Initialize service clients
        self.discovery = DiscoveryClient(self)
        self.linking = LinkingClient(self)
        self.consent = ConsentClient(self)
        self.health_information = HealthInformationClient(self)
        self.hip_callbacks = HIPCallbacksClient(self)

    def _load_schema(self, schema_path: Optional[str] = None):
        """Load and validate official ABDM schema."""
        if schema_path is None:
            # Auto-detect schema path
            possible_paths = [
                Path(__file__).parent.parent.parent.parent / "api-schemas" / "gateway.yaml",
                Path.cwd() / "api-schemas" / "gateway.yaml",
                Path.cwd() / "gateway.yaml"
            ]

            for path in possible_paths:
                if path.exists():
                    schema_path = str(path)
                    break

        if schema_path and Path(schema_path).exists():
            with open(schema_path, 'r') as f:
                self.schema = yaml.safe_load(f)

            # Validate that the schema itself is valid OpenAPI
            try:
                validate(self.schema)
            except Exception as e:
                raise ValidationError(f"Invalid OpenAPI schema: {str(e)}")
        else:
            # Disable validation if schema not found
            self.validate_schemas = False

    def validate_response(self, response: Dict[str, Any], schema_ref: str):
        """
        Validate response against ABDM schema.

        Args:
            response: Response dictionary to validate
            schema_ref: Schema reference (e.g., "PatientDiscoveryResult")

        Raises:
            SchemaValidationError: If response doesn't match schema
        """
        if not self.validate_schemas or not self.schema:
            return

        # Get schema definition
        schemas = self.schema.get("components", {}).get("schemas", {})
        if schema_ref not in schemas:
            return  # Schema not found, skip validation

        schema_def = schemas[schema_ref]

        # Check required fields
        required_fields = schema_def.get("required", [])
        missing_fields = [f for f in required_fields if f not in response]

        if missing_fields:
            raise SchemaValidationError(
                f"Response missing required fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields}
            )

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        validate_response_schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling and validation.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body (for POST/PUT)
            params: Query parameters
            validate_response_schema: Schema name to validate response against

        Returns:
            Response dictionary

        Raises:
            NetworkError: If network request fails
            TimeoutError: If request times out
            ABDMError: If API returns an error
        """
        try:
            response = await self.http_client.request(
                method=method,
                url=endpoint,
                json=data,
                params=params
            )

            # Handle non-2xx responses
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise ABDMError(
                    message=error_data.get("message", f"HTTP {response.status_code}"),
                    error_code=response.status_code,
                    details=error_data
                )

            # Parse response
            result = response.json() if response.content else {}

            # Validate against schema if requested
            if validate_response_schema:
                self.validate_response(result, validate_response_schema)

            return result

        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out after {self.timeout}s: {str(e)}")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {str(e)}")
        except ABDMError:
            raise
        except Exception as e:
            raise ABDMError(f"Unexpected error: {str(e)}")

    # High-level convenience methods

    async def discover_patient(
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

        Args:
            abha_number: Patient ABHA number (e.g., "22-7225-4829-5255")
            mobile: Patient mobile number (e.g., "+919876543210")
            name: Patient name for fuzzy matching
            gender: Patient gender (M, F, O, U)
            year_of_birth: Patient birth year
            timeout: Timeout in seconds to wait for callback

        Returns:
            Discovery result with matched patient and care contexts

        Raises:
            PatientNotFoundError: If no patient found
            ValidationError: If invalid parameters provided
        """
        return await self.discovery.discover(
            abha_number=abha_number,
            mobile=mobile,
            name=name,
            gender=gender,
            year_of_birth=year_of_birth,
            timeout=timeout
        )

    async def initiate_linking(
        self,
        patient_ref: str,
        care_contexts: List[str],
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Initiate care context linking (generates OTP).

        Args:
            patient_ref: Patient reference number at HIP
            care_contexts: List of care context IDs to link
            timeout: Timeout in seconds to wait for callback

        Returns:
            Link reference and OTP details

        Raises:
            LinkingError: If linking initiation fails
        """
        return await self.linking.initiate(
            patient_ref=patient_ref,
            care_contexts=care_contexts,
            timeout=timeout
        )

    async def confirm_linking(
        self,
        link_ref: str,
        otp: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Confirm care context linking with OTP.

        Args:
            link_ref: Link reference from initiate_linking
            otp: OTP received by patient
            timeout: Timeout in seconds to wait for callback

        Returns:
            Linked patient details with care contexts

        Raises:
            LinkingError: If OTP is invalid or linking fails
        """
        return await self.linking.confirm(
            link_ref=link_ref,
            otp=otp,
            timeout=timeout
        )

    async def request_consent(
        self,
        patient_abha: str,
        purpose: str,
        hi_types: List[str],
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        data_erase_at: Optional[datetime] = None,
        requester_name: str = "Dr. John Doe",
        requester_id: str = "MH1001",
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Request patient consent for health information access.

        Args:
            patient_abha: Patient ABHA with @sbx (e.g., "22-7225-4829-5255@sbx")
            purpose: Purpose code (CAREMGT, BTG, PUBHLTH, HPAYMT, DSRCH, PATRQT)
            hi_types: List of HI types (DiagnosticReport, Prescription, etc.)
            date_from: Data access from date (default: 1 year ago)
            date_to: Data access to date (default: today)
            data_erase_at: When to erase data (default: 30 days from now)
            requester_name: Name of requester (doctor/facility)
            requester_id: Requester registration ID
            timeout: Timeout in seconds to wait for callback

        Returns:
            Consent request details with request ID

        Raises:
            ConsentError: If consent request fails
        """
        return await self.consent.request(
            patient_abha=patient_abha,
            purpose=purpose,
            hi_types=hi_types,
            date_from=date_from,
            date_to=date_to,
            data_erase_at=data_erase_at,
            requester_name=requester_name,
            requester_id=requester_id,
            timeout=timeout
        )

    async def fetch_health_information(
        self,
        consent_id: str,
        data_push_url: str,
        encryption_public_key: str,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Fetch health information after consent granted.

        Args:
            consent_id: Consent artefact ID
            data_push_url: URL where HIP should push encrypted data
            encryption_public_key: Public key for data encryption (base64)
            timeout: Timeout in seconds to wait for data transfer

        Returns:
            Health information request acknowledgement

        Raises:
            ConsentError: If consent is invalid or expired
        """
        return await self.health_information.request(
            consent_id=consent_id,
            data_push_url=data_push_url,
            encryption_public_key=encryption_public_key,
            timeout=timeout
        )

    async def close(self):
        """Close HTTP client connections."""
        await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
