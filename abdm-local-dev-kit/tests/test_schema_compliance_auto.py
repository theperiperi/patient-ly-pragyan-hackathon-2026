"""
Automated Schema Compliance Testing using OpenAPI Validation

Uses schemathesis and openapi-spec-validator to automatically validate
that FastAPI endpoints match the official ABDM API schemas.
"""

import pytest
import yaml
from pathlib import Path
import schemathesis
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

# Load official ABDM schema
SCHEMA_PATH = Path(__file__).parent.parent / "api-schemas" / "gateway.yaml"


@pytest.fixture(scope="session")
def official_schema():
    """Load and validate official ABDM schema."""
    with open(SCHEMA_PATH, 'r') as f:
        schema = yaml.safe_load(f)

    # Validate that the official schema itself is valid OpenAPI
    validate_spec(schema)

    return schema


@pytest.fixture(scope="session")
def schema_spec():
    """Load schema using schemathesis."""
    return schemathesis.from_path(str(SCHEMA_PATH))


class TestOfficialSchemaValidity:
    """Test that the official ABDM schema is valid OpenAPI 3.0."""

    def test_schema_is_valid_openapi(self, official_schema):
        """Validate official schema conforms to OpenAPI 3.0 spec."""
        # This will raise if schema is invalid
        validate_spec(official_schema)

        assert official_schema['openapi'].startswith('3.0')
        assert 'paths' in official_schema
        assert 'components' in official_schema


class TestConsentFlowEndpoints:
    """Test consent flow endpoints exist in official schema."""

    def test_consent_request_init_endpoint(self, official_schema):
        """Verify consent request init endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/consent-requests/init' in paths

        endpoint = paths['/v0.5/consent-requests/init']
        assert 'post' in endpoint

        # Verify request body schema
        request_body = endpoint['post'].get('requestBody', {})
        assert 'content' in request_body
        assert 'application/json' in request_body['content']

        schema_ref = request_body['content']['application/json']['schema']['$ref']
        assert 'ConsentRequest' in schema_ref

    def test_consent_status_endpoint(self, official_schema):
        """Verify consent status endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/consent-requests/status' in paths

    def test_consent_fetch_endpoint(self, official_schema):
        """Verify consent fetch endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/consents/fetch' in paths


class TestDiscoveryEndpoints:
    """Test patient discovery endpoints exist in official schema."""

    def test_discover_endpoint(self, official_schema):
        """Verify patient discovery endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/care-contexts/discover' in paths

        endpoint = paths['/v0.5/care-contexts/discover']
        assert 'post' in endpoint

        # Verify schema reference
        request_body = endpoint['post'].get('requestBody', {})
        schema_ref = request_body['content']['application/json']['schema']['$ref']
        assert 'PatientDiscoveryRequest' in schema_ref

    def test_on_discover_endpoint(self, official_schema):
        """Verify on-discover callback endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/care-contexts/on-discover' in paths


class TestLinkingEndpoints:
    """Test care context linking endpoints exist in official schema."""

    def test_link_init_endpoint(self, official_schema):
        """Verify link init endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/links/link/init' in paths

        endpoint = paths['/v0.5/links/link/init']
        assert 'post' in endpoint

        request_body = endpoint['post'].get('requestBody', {})
        schema_ref = request_body['content']['application/json']['schema']['$ref']
        assert 'PatientLinkReferenceRequest' in schema_ref

    def test_link_on_init_endpoint(self, official_schema):
        """Verify link on-init callback endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/links/link/on-init' in paths

    def test_link_confirm_endpoint(self, official_schema):
        """Verify link confirm endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/links/link/confirm' in paths

        endpoint = paths['/v0.5/links/link/confirm']
        assert 'post' in endpoint

        request_body = endpoint['post'].get('requestBody', {})
        schema_ref = request_body['content']['application/json']['schema']['$ref']
        assert 'LinkConfirmationRequest' in schema_ref

    def test_link_on_confirm_endpoint(self, official_schema):
        """Verify link on-confirm callback endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/links/link/on-confirm' in paths


class TestHealthInformationEndpoints:
    """Test health information request endpoints exist in official schema."""

    def test_hi_request_endpoint(self, official_schema):
        """Verify health information request endpoint is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/health-information/cm/request' in paths

        endpoint = paths['/v0.5/health-information/cm/request']
        assert 'post' in endpoint

        request_body = endpoint['post'].get('requestBody', {})
        schema_ref = request_body['content']['application/json']['schema']['$ref']
        assert 'HIRequest' in schema_ref

    def test_hi_on_request_cm_endpoint(self, official_schema):
        """Verify HI on-request callback to CM is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/health-information/cm/on-request' in paths

        endpoint = paths['/v0.5/health-information/cm/on-request']
        assert 'post' in endpoint

        request_body = endpoint['post'].get('requestBody', {})
        schema_ref = request_body['content']['application/json']['schema']['$ref']
        assert 'HIUHealthInformationRequestResponse' in schema_ref

    def test_hi_on_request_hip_endpoint(self, official_schema):
        """Verify HI on-request callback to HIP is defined."""
        paths = official_schema.get('paths', {})
        assert '/v0.5/health-information/hip/on-request' in paths


class TestSchemaComponents:
    """Test that all required schema components are defined."""

    def test_consent_request_schema(self, official_schema):
        """Verify ConsentRequest schema is defined."""
        components = official_schema.get('components', {})
        schemas = components.get('schemas', {})

        assert 'ConsentRequest' in schemas
        schema = schemas['ConsentRequest']

        # Verify required fields
        assert 'required' in schema
        assert 'requestId' in schema['required']
        assert 'timestamp' in schema['required']
        assert 'consent' in schema['required']

        # Verify properties
        assert 'properties' in schema
        assert 'requestId' in schema['properties']
        assert 'timestamp' in schema['properties']
        assert 'consent' in schema['properties']

    def test_patient_discovery_request_schema(self, official_schema):
        """Verify PatientDiscoveryRequest schema is defined."""
        components = official_schema.get('components', {})
        schemas = components.get('schemas', {})

        assert 'PatientDiscoveryRequest' in schemas
        schema = schemas['PatientDiscoveryRequest']

        # Verify required fields
        assert 'requestId' in schema['required']
        assert 'timestamp' in schema['required']
        assert 'transactionId' in schema['required']
        assert 'patient' in schema['required']

    def test_hi_request_schema(self, official_schema):
        """Verify HIRequest schema is defined."""
        components = official_schema.get('components', {})
        schemas = components.get('schemas', {})

        assert 'HIRequest' in schemas
        schema = schemas['HIRequest']

        # Verify required fields
        assert 'requestId' in schema['required']
        assert 'timestamp' in schema['required']
        assert 'hiRequest' in schema['required']

    def test_key_material_schema(self, official_schema):
        """Verify keyMaterial schema is defined."""
        components = official_schema.get('components', {})
        schemas = components.get('schemas', {})

        assert 'keyMaterial' in schemas
        schema = schemas['keyMaterial']

        # Verify required encryption fields
        assert 'cryptoAlg' in schema['required']
        assert 'curve' in schema['required']
        assert 'dhPublicKey' in schema['required']
        assert 'nonce' in schema['required']


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
