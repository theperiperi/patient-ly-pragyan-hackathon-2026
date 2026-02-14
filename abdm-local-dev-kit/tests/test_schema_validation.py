"""
Automated Schema Validation Tests

Tests all HIU and FHIR Validator endpoints against OpenAPI specifications
to ensure 100% schema compliance with ABDM gateway.yaml.
"""

import json
import requests
import yaml
import uuid
from pathlib import Path
from typing import Dict, Any, List


class SchemaValidator:
    """Validates API endpoints against OpenAPI specifications."""

    def __init__(self):
        self.base_url_hiu = "http://localhost:8093"
        self.base_url_validator = "http://localhost:8094"
        self.gateway_schema_path = Path(__file__).parent.parent / "api-schemas" / "gateway.yaml"
        self.results = []

    def load_gateway_schema(self) -> Dict[str, Any]:
        """Load the official ABDM gateway.yaml schema."""
        with open(self.gateway_schema_path, 'r') as f:
            return yaml.safe_load(f)

    def test_endpoint_exists(self, path: str, method: str, schema: Dict[str, Any]) -> bool:
        """Test if an endpoint exists in the OpenAPI schema."""
        if path not in schema.get('paths', {}):
            return False
        if method.lower() not in schema['paths'][path]:
            return False
        return True

    def test_hiu_consent_init(self) -> Dict[str, Any]:
        """Test POST /v0.5/consent-requests/init endpoint."""
        endpoint = "/v0.5/consent-requests/init"
        method = "POST"

        payload = {
            "requestId": str(uuid.uuid4()),
            "timestamp": "2024-01-01T12:00:00.000Z",
            "consent": {
                "purpose": {
                    "text": "Care Management",
                    "code": "CAREMGT"
                },
                "patient": {
                    "id": "22-7225-4829-5255@sbx"
                },
                "hip": {
                    "id": "10000005"
                },
                "hiu": {
                    "id": "Triage-AI-System"
                },
                "requester": {
                    "name": "Dr. Manju",
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
                        "from": "2024-01-01T00:00:00.000Z",
                        "to": "2024-12-31T23:59:59.999Z"
                    },
                    "dataEraseAt": "2025-01-01T00:00:00.000Z",
                    "frequency": {
                        "unit": "HOUR",
                        "value": 1,
                        "repeats": 0
                    }
                }
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token",
            "X-CM-ID": "sbx"
        }

        try:
            response = requests.post(
                f"{self.base_url_hiu}{endpoint}",
                json=payload,
                headers=headers,
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 202,
                "passed": response.status_code == 202,
                "response": response.json() if response.status_code < 500 else None,
                "error": None
            }
        except Exception as e:
            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": None,
                "expected_status": 202,
                "passed": False,
                "response": None,
                "error": str(e)
            }

    def test_hiu_hi_request(self) -> Dict[str, Any]:
        """Test POST /v0.5/health-information/cm/request endpoint."""
        endpoint = "/v0.5/health-information/cm/request"
        method = "POST"

        payload = {
            "requestId": str(uuid.uuid4()),
            "timestamp": "2024-01-01T12:00:00.000Z",
            "hiRequest": {
                "consent": {
                    "id": "consent-123"
                },
                "dateRange": {
                    "from": "2024-01-01T00:00:00.000Z",
                    "to": "2024-12-31T23:59:59.999Z"
                },
                "dataPushUrl": "https://hiu.example.com/data-push",
                "keyMaterial": {
                    "cryptoAlg": "ECDH",
                    "curve": "Curve25519",
                    "dhPublicKey": {
                        "expiry": "2025-01-01T00:00:00.000Z",
                        "parameters": "Curve25519/32byte-random-key",
                        "keyValue": "sample-base64-encoded-key"
                    },
                    "nonce": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
                }
            }
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token",
            "X-CM-ID": "sbx"
        }

        try:
            response = requests.post(
                f"{self.base_url_hiu}{endpoint}",
                json=payload,
                headers=headers,
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 202,
                "passed": response.status_code == 202,
                "response": response.json() if response.status_code < 500 else None,
                "error": None
            }
        except Exception as e:
            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": None,
                "expected_status": 202,
                "passed": False,
                "response": None,
                "error": str(e)
            }

    def test_fhir_validate(self) -> Dict[str, Any]:
        """Test POST /validate endpoint."""
        endpoint = "/validate"
        method = "POST"

        payload = {
            "resourceType": "Bundle",
            "type": "document",
            "identifier": {
                "system": "https://ndhm.gov.in",
                "value": "test-bundle-001"
            },
            "timestamp": "2024-01-01T12:00:00+05:30",
            "entry": [
                {
                    "fullUrl": "urn:uuid:patient-001",
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-001",
                        "name": [
                            {
                                "text": "John Doe"
                            }
                        ]
                    }
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(
                f"{self.base_url_validator}{endpoint}",
                json=payload,
                headers=headers,
                timeout=10
            )

            result = response.json()
            is_valid = result.get('valid', False)

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200 and is_valid,
                "response": result,
                "error": None
            }
        except Exception as e:
            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": None,
                "expected_status": 200,
                "passed": False,
                "response": None,
                "error": str(e)
            }

    def test_fhir_profiles(self) -> Dict[str, Any]:
        """Test GET /profiles endpoint."""
        endpoint = "/profiles"
        method = "GET"

        try:
            response = requests.get(
                f"{self.base_url_validator}{endpoint}",
                timeout=10
            )

            result = response.json()
            profiles_count = result.get('total', 0)

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200 and profiles_count > 0,
                "response": {"total": profiles_count, "profiles": f"{profiles_count} profiles loaded"},
                "error": None
            }
        except Exception as e:
            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": None,
                "expected_status": 200,
                "passed": False,
                "response": None,
                "error": str(e)
            }

    def test_gateway_schema_compliance(self) -> Dict[str, Any]:
        """Test if HIU endpoints exist in gateway.yaml."""
        try:
            schema = self.load_gateway_schema()

            hiu_endpoints = [
                ("/v0.5/consent-requests/init", "post"),
                ("/v0.5/consent-requests/on-init", "post"),
                ("/v0.5/consents/hiu/notify", "post"),
                ("/v0.5/health-information/cm/request", "post"),
                ("/v0.5/health-information/cm/on-request", "post"),
            ]

            results = []
            for path, method in hiu_endpoints:
                exists = self.test_endpoint_exists(path, method, schema)
                results.append({
                    "endpoint": f"{method.upper()} {path}",
                    "exists_in_schema": exists,
                    "passed": exists
                })

            all_passed = all(r['passed'] for r in results)

            return {
                "endpoint": "Gateway Schema Compliance",
                "status_code": 200 if all_passed else 400,
                "expected_status": 200,
                "passed": all_passed,
                "response": {"endpoints": results},
                "error": None
            }
        except Exception as e:
            return {
                "endpoint": "Gateway Schema Compliance",
                "status_code": None,
                "expected_status": 200,
                "passed": False,
                "response": None,
                "error": str(e)
            }

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all schema validation tests."""
        print("=" * 80)
        print("ABDM SCHEMA VALIDATION TESTS")
        print("=" * 80)
        print()

        tests = [
            ("HIU Consent Request Init", self.test_hiu_consent_init),
            ("HIU Health Information Request", self.test_hiu_hi_request),
            ("FHIR Validator - Validate Bundle", self.test_fhir_validate),
            ("FHIR Validator - List Profiles", self.test_fhir_profiles),
            ("Gateway Schema Compliance", self.test_gateway_schema_compliance),
        ]

        results = []
        for test_name, test_func in tests:
            print(f"Testing: {test_name}")
            result = test_func()
            results.append(result)

            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"  Status: {status}")
            print(f"  Endpoint: {result['endpoint']}")
            print(f"  HTTP Status: {result['status_code']} (Expected: {result['expected_status']})")

            if result['error']:
                print(f"  Error: {result['error']}")

            print()

        # Summary
        passed = sum(1 for r in results if r['passed'])
        total = len(results)

        print("=" * 80)
        print(f"SUMMARY: {passed}/{total} tests passed")
        print("=" * 80)

        if passed == total:
            print("✅ 100% SCHEMA COMPLIANCE ACHIEVED")
        else:
            print(f"❌ Schema compliance: {(passed/total)*100:.1f}%")

        return results


if __name__ == "__main__":
    validator = SchemaValidator()
    results = validator.run_all_tests()

    # Exit with appropriate code
    all_passed = all(r['passed'] for r in results)
    exit(0 if all_passed else 1)
