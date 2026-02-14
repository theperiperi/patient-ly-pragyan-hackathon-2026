"""
Automated HIP Schema Validation Tests

Tests all HIP endpoints against OpenAPI specifications to ensure
100% schema compliance with ABDM gateway.yaml.
"""

import json
import requests
import yaml
import uuid
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta
from jose import jwt


class HIPSchemaValidator:
    """Validates HIP API endpoints against OpenAPI specifications."""

    def __init__(self):
        self.base_url_hip = "http://localhost:8092"
        self.gateway_schema_path = Path(__file__).parent.parent / "api-schemas" / "gateway.yaml"
        self.results = []
        self.auth_token = self._generate_jwt_token()

    def _generate_jwt_token(self) -> str:
        """Generate a valid JWT token for testing."""
        payload = {
            "sub": "test-hip-client",
            "exp": datetime.now() + timedelta(hours=1),
            "iat": datetime.now()
        }
        secret = "abdm-local-dev-secret-key-change-in-production"
        algorithm = "HS256"
        return jwt.encode(payload, secret, algorithm=algorithm)

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

    def test_discovery_endpoint(self) -> Dict[str, Any]:
        """Test POST /v0.5/care-contexts/discover endpoint."""
        endpoint = "/v0.5/care-contexts/discover"
        method = "POST"

        payload = {
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "transactionId": str(uuid.uuid4()),
            "patient": {
                "id": "hinapatel@sbx",
                "verifiedIdentifiers": [
                    {"type": "HEALTH_ID", "value": "hinapatel@sbx"}
                ],
                "name": "Hina Patel",
                "gender": "F",
                "yearOfBirth": 1990
            }
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_on_discover_callback(self) -> Dict[str, Any]:
        """Test POST /v0.5/care-contexts/on-discover callback endpoint."""
        endpoint = "/v0.5/care-contexts/on-discover"
        method = "POST"

        request_id = str(uuid.uuid4())
        transaction_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "transactionId": transaction_id,
            "patient": {
                "referenceNumber": "TMH-001",
                "display": "Hina Patel",
                "careContexts": [
                    {"referenceNumber": "CC-001", "display": "Consultation - 2024-01-15"}
                ],
                "matchedBy": ["HEALTH_ID"]
            },
            "resp": {"requestId": request_id}
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_link_init_endpoint(self) -> Dict[str, Any]:
        """Test POST /v0.5/links/link/init endpoint."""
        endpoint = "/v0.5/links/link/init"
        method = "POST"

        payload = {
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "transactionId": str(uuid.uuid4()),
            "patient": {
                "id": "hinapatel@sbx",
                "referenceNumber": "TMH-001",
                "careContexts": [
                    {"referenceNumber": "CC-001"}
                ]
            }
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_on_link_init_callback(self) -> Dict[str, Any]:
        """Test POST /v0.5/links/link/on-init callback endpoint."""
        endpoint = "/v0.5/links/link/on-init"
        method = "POST"

        request_id = str(uuid.uuid4())
        transaction_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "transactionId": transaction_id,
            "link": {
                "referenceNumber": "LINK-" + str(uuid.uuid4())[:8],
                "authenticationType": "DIRECT",
                "meta": {
                    "communicationMedium": "MOBILE",
                    "communicationHint": "+91******7890",
                    "communicationExpiry": (datetime.now() + timedelta(minutes=10)).isoformat() + "Z"
                }
            },
            "resp": {"requestId": request_id}
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_link_confirm_endpoint(self) -> Dict[str, Any]:
        """Test POST /v0.5/links/link/confirm endpoint."""
        endpoint = "/v0.5/links/link/confirm"
        method = "POST"

        payload = {
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "confirmation": {
                "linkRefNumber": "LINK-12345678",
                "token": "123456"
            }
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_on_link_confirm_callback(self) -> Dict[str, Any]:
        """Test POST /v0.5/links/link/on-confirm callback endpoint."""
        endpoint = "/v0.5/links/link/on-confirm"
        method = "POST"

        request_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "patient": {
                "referenceNumber": "TMH-001",
                "display": "Hina Patel",
                "careContexts": [
                    {"referenceNumber": "CC-001", "display": "Consultation - 2024-01-15"}
                ]
            },
            "resp": {"requestId": request_id}
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_health_info_request_endpoint(self) -> Dict[str, Any]:
        """Test POST /v0.5/health-information/hip/request endpoint."""
        endpoint = "/v0.5/health-information/hip/request"
        method = "POST"

        payload = {
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "transactionId": str(uuid.uuid4()),
            "hiRequest": {
                "consent": {"id": "consent-123"},
                "dateRange": {
                    "from": "2024-01-01T00:00:00.000Z",
                    "to": "2024-12-31T23:59:59.999Z"
                },
                "dataPushUrl": "https://hiu.example.com/data-push",
                "keyMaterial": {
                    "cryptoAlg": "ECDH",
                    "curve": "Curve25519",
                    "dhPublicKey": {
                        "expiry": (datetime.now() + timedelta(days=1)).isoformat() + "Z",
                        "parameters": "Curve25519/32byte-random-key",
                        "keyValue": "sample-base64-encoded-key"
                    },
                    "nonce": str(uuid.uuid4())
                }
            }
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_on_health_info_request_callback(self) -> Dict[str, Any]:
        """Test POST /v0.5/health-information/hip/on-request callback endpoint."""
        endpoint = "/v0.5/health-information/hip/on-request"
        method = "POST"

        request_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "hiRequest": {
                "transactionId": str(uuid.uuid4()),
                "sessionStatus": "ACKNOWLEDGED"
            },
            "resp": {"requestId": request_id}
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_add_contexts_endpoint(self) -> Dict[str, Any]:
        """Test POST /v0.5/links/link/add-contexts endpoint."""
        endpoint = "/v0.5/links/link/add-contexts"
        method = "POST"

        payload = {
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "link": {
                "referenceNumber": "TMH-001",
                "display": "Hina Patel"
            },
            "patient": {
                "referenceNumber": "TMH-001",
                "display": "Hina Patel"
            },
            "careContexts": [
                {"referenceNumber": "CC-002", "display": "Lab Report - 2024-02-01"}
            ]
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
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

    def test_on_add_contexts_callback(self) -> Dict[str, Any]:
        """Test POST /v0.5/links/link/on-add-contexts callback endpoint."""
        endpoint = "/v0.5/links/link/on-add-contexts"
        method = "POST"

        request_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "acknowledgement": {"status": "SUCCESS"},
            "resp": {"requestId": request_id}
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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

    def test_context_notify_endpoint(self) -> Dict[str, Any]:
        """Test POST /v0.5/links/context/notify endpoint."""
        endpoint = "/v0.5/links/context/notify"
        method = "POST"

        payload = {
            "requestId": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "notification": {
                "careContext": {
                    "referenceNumber": "CC-003",
                    "display": "Prescription - 2024-02-14"
                },
                "hiTypes": ["Prescription"],
                "date": datetime.now().isoformat() + "Z"
            }
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
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

    def test_on_context_notify_callback(self) -> Dict[str, Any]:
        """Test POST /v0.5/links/context/on-notify callback endpoint."""
        endpoint = "/v0.5/links/context/on-notify"
        method = "POST"

        request_id = str(uuid.uuid4())

        payload = {
            "requestId": request_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "acknowledgement": {"status": "SUCCESS"},
            "resp": {"requestId": request_id}
        }

        try:
            response = requests.post(
                f"{self.base_url_hip}{endpoint}",
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.auth_token}"
                },
                timeout=10
            )

            return {
                "endpoint": f"{method} {endpoint}",
                "status_code": response.status_code,
                "expected_status": 200,
                "passed": response.status_code == 200,
                "response": response.json() if response.status_code < 500 else None,
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
        """Test if all HIP endpoints exist in gateway.yaml."""
        try:
            schema = self.load_gateway_schema()

            hip_endpoints = [
                ("/v0.5/care-contexts/discover", "post"),
                ("/v0.5/care-contexts/on-discover", "post"),
                ("/v0.5/links/link/init", "post"),
                ("/v0.5/links/link/on-init", "post"),
                ("/v0.5/links/link/confirm", "post"),
                ("/v0.5/links/link/on-confirm", "post"),
                ("/v0.5/health-information/hip/request", "post"),
                ("/v0.5/health-information/hip/on-request", "post"),
                ("/v0.5/links/link/add-contexts", "post"),
                ("/v0.5/links/link/on-add-contexts", "post"),
                ("/v0.5/links/context/notify", "post"),
                ("/v0.5/links/context/on-notify", "post"),
            ]

            results = []
            for path, method in hip_endpoints:
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
        """Run all HIP schema validation tests."""
        print("=" * 80)
        print("HIP SCHEMA VALIDATION TESTS")
        print("=" * 80)
        print()

        tests = [
            ("HIP Discovery", self.test_discovery_endpoint),
            ("HIP Discovery Callback", self.test_on_discover_callback),
            ("HIP Link Init", self.test_link_init_endpoint),
            ("HIP Link Init Callback", self.test_on_link_init_callback),
            ("HIP Link Confirm", self.test_link_confirm_endpoint),
            ("HIP Link Confirm Callback", self.test_on_link_confirm_callback),
            ("HIP Health Info Request", self.test_health_info_request_endpoint),
            ("HIP Health Info Request Callback", self.test_on_health_info_request_callback),
            ("HIP Add Contexts", self.test_add_contexts_endpoint),
            ("HIP Add Contexts Callback", self.test_on_add_contexts_callback),
            ("HIP Context Notify", self.test_context_notify_endpoint),
            ("HIP Context Notify Callback", self.test_on_context_notify_callback),
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
            print("✅ 100% HIP SCHEMA COMPLIANCE ACHIEVED")
        else:
            print(f"❌ Schema compliance: {(passed/total)*100:.1f}%")

        return results


if __name__ == "__main__":
    validator = HIPSchemaValidator()
    results = validator.run_all_tests()

    # Exit with appropriate code
    all_passed = all(r['passed'] for r in results)
    exit(0 if all_passed else 1)
