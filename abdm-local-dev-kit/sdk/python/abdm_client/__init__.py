"""
ABDM Python Client Library

A production-ready Python SDK for ABDM (Ayushman Bharat Digital Mission) health data exchange.
Includes built-in schema validation and comprehensive error handling.

Usage:
    from abdm_client import ABDMClient

    client = ABDMClient(
        base_url="http://localhost:8090",
        client_id="demo-hiu",
        client_secret="demo-secret"
    )

    # Discover patient
    result = client.discover_patient(
        abha_number="22-7225-4829-5255",
        name="John Doe",
        gender="M",
        year_of_birth=1990
    )

    # Link care contexts with OTP
    link_ref = client.initiate_linking(
        patient_ref="PATIENT-001",
        care_contexts=["EPISODE-001", "EPISODE-002"]
    )

    # Confirm with OTP
    client.confirm_linking(link_ref, otp="123456")

    # Request consent
    consent = client.request_consent(
        patient_abha="22-7225-4829-5255@sbx",
        purpose="CAREMGT",
        hi_types=["DiagnosticReport", "Prescription"]
    )

    # Fetch health information
    records = client.fetch_health_information(consent_id)
"""

from .client import ABDMClient
from .hip_callbacks import HIPCallbacksClient
from .exceptions import (
    ABDMError,
    ValidationError,
    AuthenticationError,
    PatientNotFoundError,
    ConsentError,
    LinkingError,
    SchemaValidationError
)

__version__ = "1.0.0"
__all__ = [
    "ABDMClient",
    "HIPCallbacksClient",
    "ABDMError",
    "ValidationError",
    "AuthenticationError",
    "PatientNotFoundError",
    "ConsentError",
    "LinkingError",
    "SchemaValidationError"
]
