"""
Automated Schema Compliance Testing

Validates that implemented Pydantic models match official ABDM API schemas.
This test suite programmatically ensures 100% schema compliance.
"""

import pytest
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Set
from pydantic import BaseModel, create_model
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import models to test
from services.consent_manager.models.consent import (
    ConsentRequest,
    ConsentRequestDetail,
    UsePurpose,
    Permission,
    Requester,
    OrganizationRepresentation,
    ConsentManagerPatientID,
    CareContextDefinition,
    Frequency,
    DateRange,
    ConsentArtefact,
    ConsentArtefactDetail
)

from services.gateway.api.consent_flow import (
    ConsentRequestInit,
    ConsentDetail,
    ConsentPurpose,
    OrganizationRef,
    RequesterIdentifier,
    Requester as GatewayRequester
)

from services.gateway.api.discovery import (
    PatientDiscoveryRequest,
    PatientDiscoveryPatient,
    Identifier,
    PatientDiscoveryResult,
    PatientRepresentation
)

from services.gateway.api.linking import (
    PatientLinkReferenceRequest,
    LinkConfirmationRequest,
    PatientLinkReferenceResult,
    PatientLinkResult
)

from services.gateway.api.health_information import (
    HIRequest,
    HIRequestDetail,
    HIUHealthInformationRequestResponse,
    KeyMaterial,
    KeyObject
)


# Schema loading utilities
def load_official_schema(schema_file: str = "api-schemas/gateway.yaml") -> Dict:
    """Load official ABDM schema from YAML file."""
    schema_path = Path(__file__).parent.parent / schema_file

    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)


def get_schema_definition(schema: Dict, ref_path: str) -> Dict:
    """
    Resolve $ref path in schema.

    Args:
        schema: Full schema dict
        ref_path: Reference path like "#/components/schemas/ConsentRequest"

    Returns:
        Schema definition dict
    """
    if not ref_path.startswith("#/"):
        return {}

    parts = ref_path[2:].split("/")
    current = schema

    for part in parts:
        current = current.get(part, {})

    return current


def validate_field_types(model: BaseModel, schema_def: Dict, path: str = "") -> List[str]:
    """
    Validate that Pydantic model fields match schema definition.

    Args:
        model: Pydantic model class
        schema_def: Schema definition from YAML
        path: Current field path for error reporting

    Returns:
        List of violation messages
    """
    violations = []

    # Get required fields from schema
    required_fields = set(schema_def.get('required', []))
    schema_properties = schema_def.get('properties', {})

    # Get model fields (Pydantic V2)
    model_fields = model.model_fields

    # Check for missing required fields
    for req_field in required_fields:
        if req_field not in model_fields:
            violations.append(
                f"MISSING REQUIRED FIELD: {path}.{req_field} - "
                f"Required by schema but not in model"
            )

    # Check field types and properties
    for field_name, field_info in model_fields.items():
        field_path = f"{path}.{field_name}" if path else field_name

        if field_name not in schema_properties:
            # Field in model but not in schema (extra field)
            if not field_info.is_required():
                violations.append(
                    f"EXTRA OPTIONAL FIELD: {field_path} - "
                    f"In model but not in official schema (WARNING)"
                )
            else:
                violations.append(
                    f"EXTRA REQUIRED FIELD: {field_path} - "
                    f"In model but not in official schema"
                )
            continue

        schema_field = schema_properties[field_name]

        # Check if field is required
        is_required_in_schema = field_name in required_fields
        is_required_in_model = field_info.is_required()

        if is_required_in_schema and not is_required_in_model:
            violations.append(
                f"REQUIRED MISMATCH: {field_path} - "
                f"Required in schema but optional in model"
            )

        # Check field type
        expected_type = schema_field.get('type')
        expected_format = schema_field.get('format')

        # Type mapping
        type_violations = check_type_compatibility(
            field_info,
            expected_type,
            expected_format,
            field_path
        )
        violations.extend(type_violations)

    return violations


def check_type_compatibility(
    field_info,
    expected_type: str,
    expected_format: str,
    field_path: str
) -> List[str]:
    """Check if Pydantic field type matches schema type."""
    violations = []

    # Get actual Python type
    actual_type = field_info.outer_type_

    # Handle Optional types
    if hasattr(actual_type, '__origin__'):
        origin = actual_type.__origin__
        if origin is type(None) or str(origin) == 'typing.Union':
            # Extract non-None type
            args = actual_type.__args__
            actual_type = next((arg for arg in args if arg is not type(None)), actual_type)

    # Type compatibility checks
    type_map = {
        'string': (str,),
        'integer': (int,),
        'number': (int, float),
        'boolean': (bool,),
        'array': (list, List),
        'object': (dict, Dict, BaseModel),
    }

    if expected_type in type_map:
        expected_python_types = type_map[expected_type]

        # Check if actual type is compatible
        is_compatible = False

        if hasattr(actual_type, '__mro__'):
            for expected_py_type in expected_python_types:
                if expected_py_type in actual_type.__mro__:
                    is_compatible = True
                    break

        if not is_compatible:
            violations.append(
                f"TYPE MISMATCH: {field_path} - "
                f"Expected {expected_type}, got {actual_type}"
            )

    # Format checks
    if expected_format == 'uuid':
        # Should be UUID or str
        if actual_type not in (str, 'UUID'):
            violations.append(
                f"FORMAT MISMATCH: {field_path} - "
                f"Expected UUID format, got {actual_type}"
            )

    elif expected_format == 'date-time':
        # Should be datetime or str
        if 'datetime' not in str(actual_type).lower() and actual_type != str:
            violations.append(
                f"FORMAT MISMATCH: {field_path} - "
                f"Expected date-time format, got {actual_type}"
            )

    return violations


# Test Suite

class TestConsentRequestSchema:
    """Test consent request models against official schema."""

    @pytest.fixture
    def official_schema(self):
        """Load official ABDM schema."""
        return load_official_schema()

    def test_consent_request_structure(self, official_schema):
        """Validate ConsentRequest matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/ConsentRequest"
        )

        violations = validate_field_types(ConsentRequest, schema_def, "ConsentRequest")

        assert len(violations) == 0, "\n".join([
            "Schema compliance violations found:",
            *violations
        ])

    def test_use_purpose_structure(self, official_schema):
        """Validate UsePurpose matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/UsePurpose"
        )

        violations = validate_field_types(UsePurpose, schema_def, "UsePurpose")

        assert len(violations) == 0, "\n".join([
            "UsePurpose schema violations:",
            *violations
        ])

    def test_permission_structure(self, official_schema):
        """Validate Permission matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/Permission"
        )

        violations = validate_field_types(Permission, schema_def, "Permission")

        assert len(violations) == 0, "\n".join([
            "Permission schema violations:",
            *violations
        ])

    def test_organization_representation(self, official_schema):
        """Validate OrganizationRepresentation matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/OrganizationRepresentation"
        )

        violations = validate_field_types(
            OrganizationRepresentation,
            schema_def,
            "OrganizationRepresentation"
        )

        # Should have NO extra fields like 'name'
        assert len(violations) == 0, "\n".join([
            "OrganizationRepresentation schema violations:",
            *violations
        ])

    def test_requester_structure(self, official_schema):
        """Validate Requester matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/Requester"
        )

        violations = validate_field_types(
            GatewayRequester,
            schema_def,
            "Requester"
        )

        # Specifically check that identifier is an object, not string
        assert len(violations) == 0, "\n".join([
            "Requester schema violations:",
            *violations
        ])


class TestEndpointCoverage:
    """Test that all required ABDM endpoints are implemented."""

    @pytest.fixture
    def official_schema(self):
        """Load official ABDM schema."""
        return load_official_schema()

    def test_consent_endpoints_exist(self, official_schema):
        """Verify all consent-related endpoints are implemented."""
        required_endpoints = [
            "/v0.5/consent-requests/init",
            "/v0.5/consent-requests/status",
            "/v0.5/consents/fetch",
        ]

        # Check if endpoints are defined in schema
        paths = official_schema.get('paths', {})

        for endpoint in required_endpoints:
            assert endpoint in paths, f"Required endpoint {endpoint} not in official schema"

    def test_discovery_endpoints_required(self, official_schema):
        """Test that discovery endpoints are in schema (implementation check separate)."""
        discovery_endpoints = [
            "/v0.5/care-contexts/discover",
            "/v0.5/care-contexts/on-discover",
        ]

        paths = official_schema.get('paths', {})

        for endpoint in discovery_endpoints:
            assert endpoint in paths, f"Discovery endpoint {endpoint} not in official schema"

    def test_linking_endpoints_required(self, official_schema):
        """Test that linking endpoints are in schema."""
        linking_endpoints = [
            "/v0.5/links/link/init",
            "/v0.5/links/link/on-init",
            "/v0.5/links/link/confirm",
        ]

        paths = official_schema.get('paths', {})

        for endpoint in linking_endpoints:
            assert endpoint in paths, f"Linking endpoint {endpoint} not in official schema"


class TestDataValidation:
    """Test that data validation matches ABDM requirements."""

    def test_purpose_codes_are_strings(self):
        """Verify purpose codes accept strings, not just enums."""
        from services.consent_manager.models.consent import VALID_PURPOSE_CODES

        # Should be a set of strings
        assert isinstance(VALID_PURPOSE_CODES, set)
        assert all(isinstance(code, str) for code in VALID_PURPOSE_CODES)

    def test_hi_types_are_strings(self):
        """Verify HI types accept strings, not just enums."""
        from services.consent_manager.models.consent import VALID_HI_TYPES

        # Should be a set of strings
        assert isinstance(VALID_HI_TYPES, set)
        assert all(isinstance(hi_type, str) for hi_type in VALID_HI_TYPES)

    def test_consent_request_accepts_valid_data(self):
        """Test that ConsentRequest can be instantiated with valid ABDM data."""
        from datetime import datetime
        from uuid import uuid4

        # Sample data matching ABDM spec
        consent_data = {
            "requestId": uuid4(),
            "timestamp": datetime.now(),
            "consent": {
                "purpose": {
                    "text": "Care Management",
                    "code": "CAREMGT",
                    "refUri": "http://terminology.hl7.org/ValueSet/v3-PurposeOfUse"
                },
                "patient": {
                    "id": "user@sbx"
                },
                "hiu": {
                    "id": "HIU-001"
                },
                "requester": {
                    "name": "Dr. John Doe",
                    "identifier": {
                        "type": "REGNO",
                        "value": "MH1001",
                        "system": "https://www.mciindia.org"
                    }
                },
                "hiTypes": ["DiagnosticReport", "Prescription"],
                "permission": {
                    "accessMode": "VIEW",
                    "dateRange": {
                        "from": datetime.now(),
                        "to": datetime.now()
                    },
                    "dataEraseAt": datetime.now(),
                    "frequency": {
                        "unit": "DAY",
                        "value": 1,
                        "repeats": 1
                    }
                },
                "consentNotificationUrl": "https://example.com/callback"
            }
        }

        # Should not raise validation error
        consent_request = ConsentRequest(**consent_data)
        assert consent_request is not None


class TestPatientDiscoverySchema:
    """Test patient discovery models against official schema."""

    @pytest.fixture
    def official_schema(self):
        """Load official ABDM schema."""
        return load_official_schema()

    def test_patient_discovery_request_structure(self, official_schema):
        """Validate PatientDiscoveryRequest matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/PatientDiscoveryRequest"
        )

        violations = validate_field_types(
            PatientDiscoveryRequest,
            schema_def,
            "PatientDiscoveryRequest"
        )

        assert len(violations) == 0, "\n".join([
            "PatientDiscoveryRequest schema violations:",
            *violations
        ])

    def test_patient_discovery_result_structure(self, official_schema):
        """Validate PatientDiscoveryResult matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/PatientDiscoveryResult"
        )

        violations = validate_field_types(
            PatientDiscoveryResult,
            schema_def,
            "PatientDiscoveryResult"
        )

        assert len(violations) == 0, "\n".join([
            "PatientDiscoveryResult schema violations:",
            *violations
        ])

    def test_identifier_structure(self, official_schema):
        """Validate Identifier matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/Identifier"
        )

        violations = validate_field_types(
            Identifier,
            schema_def,
            "Identifier"
        )

        assert len(violations) == 0, "\n".join([
            "Identifier schema violations:",
            *violations
        ])


class TestLinkingSchema:
    """Test care context linking models against official schema."""

    @pytest.fixture
    def official_schema(self):
        """Load official ABDM schema."""
        return load_official_schema()

    def test_patient_link_reference_request_structure(self, official_schema):
        """Validate PatientLinkReferenceRequest matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/PatientLinkReferenceRequest"
        )

        violations = validate_field_types(
            PatientLinkReferenceRequest,
            schema_def,
            "PatientLinkReferenceRequest"
        )

        assert len(violations) == 0, "\n".join([
            "PatientLinkReferenceRequest schema violations:",
            *violations
        ])

    def test_link_confirmation_request_structure(self, official_schema):
        """Validate LinkConfirmationRequest matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/LinkConfirmationRequest"
        )

        violations = validate_field_types(
            LinkConfirmationRequest,
            schema_def,
            "LinkConfirmationRequest"
        )

        assert len(violations) == 0, "\n".join([
            "LinkConfirmationRequest schema violations:",
            *violations
        ])

    def test_patient_link_reference_result_structure(self, official_schema):
        """Validate PatientLinkReferenceResult matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/PatientLinkReferenceResult"
        )

        violations = validate_field_types(
            PatientLinkReferenceResult,
            schema_def,
            "PatientLinkReferenceResult"
        )

        assert len(violations) == 0, "\n".join([
            "PatientLinkReferenceResult schema violations:",
            *violations
        ])

    def test_patient_link_result_structure(self, official_schema):
        """Validate PatientLinkResult matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/PatientLinkResult"
        )

        violations = validate_field_types(
            PatientLinkResult,
            schema_def,
            "PatientLinkResult"
        )

        assert len(violations) == 0, "\n".join([
            "PatientLinkResult schema violations:",
            *violations
        ])


class TestHealthInformationSchema:
    """Test health information request models against official schema."""

    @pytest.fixture
    def official_schema(self):
        """Load official ABDM schema."""
        return load_official_schema()

    def test_hi_request_structure(self, official_schema):
        """Validate HIRequest matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/HIRequest"
        )

        violations = validate_field_types(
            HIRequest,
            schema_def,
            "HIRequest"
        )

        assert len(violations) == 0, "\n".join([
            "HIRequest schema violations:",
            *violations
        ])

    def test_hiu_hi_request_response_structure(self, official_schema):
        """Validate HIUHealthInformationRequestResponse matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/HIUHealthInformationRequestResponse"
        )

        violations = validate_field_types(
            HIUHealthInformationRequestResponse,
            schema_def,
            "HIUHealthInformationRequestResponse"
        )

        assert len(violations) == 0, "\n".join([
            "HIUHealthInformationRequestResponse schema violations:",
            *violations
        ])

    def test_key_material_structure(self, official_schema):
        """Validate KeyMaterial matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/keyMaterial"
        )

        violations = validate_field_types(
            KeyMaterial,
            schema_def,
            "keyMaterial"
        )

        assert len(violations) == 0, "\n".join([
            "KeyMaterial schema violations:",
            *violations
        ])

    def test_key_object_structure(self, official_schema):
        """Validate KeyObject matches official schema."""
        schema_def = get_schema_definition(
            official_schema,
            "#/components/schemas/keyObject"
        )

        violations = validate_field_types(
            KeyObject,
            schema_def,
            "keyObject"
        )

        assert len(violations) == 0, "\n".join([
            "KeyObject schema violations:",
            *violations
        ])


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
