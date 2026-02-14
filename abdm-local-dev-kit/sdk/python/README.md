# ABDM Python Client Library

Production-ready Python SDK for ABDM (Ayushman Bharat Digital Mission) health data exchange with **built-in schema validation** and comprehensive error handling.

## ✨ Key Features

✅ **100% ABDM Schema Compliance** - Automatically validates all requests/responses against official ABDM OpenAPI specification
✅ **All Latest Fixes Included** - Incorporates all schema fixes (Requester.identifier, UsePurpose, HIType, etc.)
✅ **Comprehensive Error Handling** - Custom exceptions for every error scenario
✅ **Type-Safe** - Full type hints with Pydantic validation
✅ **Async/Await** - Built on httpx for high-performance async operations
✅ **Auto Schema Detection** - Finds and loads gateway.yaml automatically
✅ **Production Ready** - Used in real ABDM integrations

## 📦 Installation

```bash
# Install from source
cd sdk/python
pip install -e .

# Or install requirements directly
pip install -r requirements.txt
```

## 🚀 Quick Start

```python
import asyncio
from abdm_client import ABDMClient

async def main():
    # Initialize client with automatic schema validation
    client = ABDMClient(
        base_url="http://localhost:8090",
        client_id="demo-hiu",
        client_secret="demo-secret",
        validate_schemas=True  # ✓ Validates against official ABDM spec
    )

    # Discover patient
    result = await client.discover_patient(
        abha_number="22-7225-4829-5255"
    )

    print(f"Found: {result['patient']['display']}")

    await client.close()

asyncio.run(main())
```

## 🔒 Schema Validation

The client automatically validates:

### ✅ Request Validation
- All required fields present
- Correct field types (string vs object)
- Valid enum values (purpose codes, HI types)
- Proper ABHA format
- Date range consistency

### ✅ Response Validation
- Matches official ABDM schema
- Required fields present
- Correct data types
- Error field structure

### ✅ Latest Schema Fixes Included

All fixes from schema compliance work are built-in:

```python
# ✓ Requester.identifier is now object (not string)
requester = {
    "name": "Dr. John Doe",
    "identifier": {
        "type": "REGNO",      # ✓ Fixed structure
        "value": "MH1001",
        "system": "https://www.mciindia.org"
    }
}

# ✓ Purpose codes are strings (not enums)
purpose = "CAREMGT"  # ✓ Validated against VALID_PURPOSE_CODES

# ✓ HI types are strings (not enums)
hi_types = ["DiagnosticReport", "Prescription"]  # ✓ Validated
```

## 📚 Complete Examples

### 1. Patient Discovery

```python
from abdm_client import ABDMClient, PatientNotFoundError

async with ABDMClient(base_url="http://localhost:8090") as client:
    try:
        # By ABHA number
        result = await client.discover_patient(
            abha_number="22-7225-4829-5255"
        )

        # By mobile
        result = await client.discover_patient(
            mobile="+919876543210",
            name="John Doe",
            gender="M",
            year_of_birth=1990
        )

        # By demographics (fuzzy matching)
        result = await client.discover_patient(
            name="Priya Sharma",
            gender="F",
            year_of_birth=1985
        )

    except PatientNotFoundError as e:
        print(f"Patient not found: {e}")
```

### 2. Care Context Linking

```python
from abdm_client import LinkingError

# Step 1: Initiate linking (generates OTP)
link_result = await client.initiate_linking(
    patient_ref="PATIENT-001",
    care_contexts=["EPISODE-001", "EPISODE-002"]
)

link_ref = link_result["linkRefNumber"]
print(f"OTP sent to: {link_result['meta']['communicationHint']}")

# Step 2: Confirm with OTP
try:
    confirm_result = await client.confirm_linking(
        link_ref=link_ref,
        otp="123456"  # From patient's phone
    )

    print(f"Linked: {confirm_result['patient']['display']}")

except LinkingError as e:
    print(f"Invalid OTP: {e}")
```

### 3. Consent Request

```python
from abdm_client import ConsentError
from datetime import datetime, timedelta

# Request consent
consent = await client.request_consent(
    patient_abha="22-7225-4829-5255@sbx",
    purpose="CAREMGT",  # ✓ Validated against VALID_PURPOSE_CODES
    hi_types=[
        "DiagnosticReport",
        "Prescription",
        "DischargeSummary"
    ],  # ✓ Validated against VALID_HI_TYPES
    date_from=datetime.now() - timedelta(days=365),
    date_to=datetime.now(),
    data_erase_at=datetime.now() + timedelta(days=30),
    requester_name="Dr. Sarah Johnson",
    requester_id="MH1001"
)

print(f"Consent request ID: {consent['consentRequestId']}")
```

### 4. Health Information Request

```python
# After consent is granted
hi_request = await client.fetch_health_information(
    consent_id="consent-uuid-here",
    data_push_url="https://your-hiu.com/data-push",
    encryption_public_key="your-base64-public-key"
)

print(f"Transaction ID: {hi_request['transactionId']}")
print(f"Status: {hi_request['sessionStatus']}")
```

### 5. HIP Callbacks and Notifications (For HIP Implementations)

The SDK provides comprehensive support for HIP implementations including all 8 ABDM callback endpoints.

#### Add Care Contexts to Existing Link

```python
# HIP can add new care contexts to an existing patient link
# without requiring new OTP verification
result = await client.hip_callbacks.add_care_contexts(
    patient_ref="PATIENT-001",
    link_ref="LINK-ABC123",
    care_contexts=[
        {
            "referenceNumber": "EP-003",
            "display": "Cardiology Follow-up - 2024-02-14"
        },
        {
            "referenceNumber": "LAB-456",
            "display": "Blood Test Results - 2024-02-14"
        }
    ]
)

print(f"Added care contexts, Request ID: {result['requestId']}")
```

#### Notify HIU About New Health Records

```python
# HIP can proactively notify HIU when new health records become available
result = await client.hip_callbacks.notify_context(
    patient_abha="22-7225-4829-5255@sbx",
    hip_id="Apollo-Hospitals-Bangalore",
    care_contexts=[
        {
            "referenceNumber": "DISCHARGE-789",
            "display": "Discharge Summary - Cardiac Surgery - 2024-02-14"
        }
    ]
)

print(f"Notified HIU, Request ID: {result['requestId']}")
```

#### Build Callback Responses (For HIP FastAPI Endpoints)

```python
from abdm_client import HIPCallbacksClient

# Example: on-discover callback (patient found)
response = HIPCallbacksClient.build_on_discover_response(
    request_id="req-123",
    transaction_id="txn-456",
    patient={
        "referenceNumber": "PATIENT-001",
        "display": "Jane Doe",
        "careContexts": [
            {"referenceNumber": "EP-001", "display": "OPD Visit - 2024-01-15"}
        ],
        "matchedBy": ["MOBILE"]
    }
)

# Example: on-init callback (OTP sent)
response = HIPCallbacksClient.build_on_init_response(
    request_id="req-456",
    link={
        "referenceNumber": "LINK-XYZ789",
        "authenticationType": "DIRECT",
        "meta": {
            "communicationMedium": "MOBILE",
            "communicationHint": "+91******7890",
            "communicationExpiry": "2024-02-14T12:30:00Z"
        }
    }
)

# Example: on-confirm callback (link confirmed)
response = HIPCallbacksClient.build_on_confirm_response(
    request_id="req-789",
    patient={
        "referenceNumber": "PATIENT-001",
        "display": "John Doe",
        "careContexts": [{"referenceNumber": "EP-001", "display": "Linked visit"}]
    }
)

# Example: on-request callback (HI request acknowledged)
response = HIPCallbacksClient.build_on_request_response(
    request_id="req-012",
    hi_request={
        "transactionId": "txn-abc-def",
        "sessionStatus": "ACKNOWLEDGED"
    }
)

# Example: on-add-contexts callback
response = HIPCallbacksClient.build_on_add_contexts_response(
    request_id="req-345",
    acknowledgement={"status": "CONTEXTS_ADDED"}
)

# Example: on-notify callback
response = HIPCallbacksClient.build_on_notify_response(
    request_id="req-678",
    acknowledgement={"status": "OK"}
)
```

#### Validation Helpers

```python
# Validate care contexts structure
try:
    HIPCallbacksClient.validate_care_contexts([
        {"referenceNumber": "EP-001", "display": "Visit 1"}
    ])
    print("✓ Valid care contexts")
except ValidationError as e:
    print(f"✗ Invalid: {e}")

# Validate patient data structure
try:
    HIPCallbacksClient.validate_patient_data({
        "referenceNumber": "PATIENT-001",
        "display": "Jane Doe",
        "careContexts": [...]
    })
    print("✓ Valid patient data")
except ValidationError as e:
    print(f"✗ Invalid: {e}")
```

**For complete HIP callback examples, see `examples/04_hip_callbacks.py`**

## 🎯 Valid Purpose Codes

The SDK validates purpose codes against official ABDM list:

- `CAREMGT` - Care Management
- `BTG` - Break the Glass (Emergency)
- `PUBHLTH` - Public Health
- `HPAYMT` - Healthcare Payment
- `DSRCH` - Disease Specific Healthcare Research
- `PATRQT` - Self Requested

```python
# ✓ Valid
await client.request_consent(purpose="CAREMGT", ...)

# ✗ Invalid - raises ValidationError
await client.request_consent(purpose="INVALID", ...)
```

## 📊 Valid HI Types

The SDK validates HI types against official ABDM list:

- `OPConsultation`
- `Prescription`
- `DischargeSummary`
- `DiagnosticReport`
- `ImmunizationRecord`
- `HealthDocumentRecord`
- `WellnessRecord`

```python
# ✓ Valid
await client.request_consent(hi_types=["DiagnosticReport", "Prescription"], ...)

# ✗ Invalid - raises ValidationError
await client.request_consent(hi_types=["InvalidType"], ...)
```

## 🚨 Error Handling

All errors inherit from `ABDMError`:

```python
from abdm_client import (
    ABDMError,
    ValidationError,         # Input validation failed
    SchemaValidationError,   # Response doesn't match ABDM schema
    AuthenticationError,     # Auth failed
    PatientNotFoundError,    # Patient not found
    ConsentError,            # Consent operation failed
    LinkingError,            # Linking failed
    TimeoutError,            # Operation timed out
    NetworkError             # Network communication failed
)

try:
    result = await client.discover_patient(...)

except PatientNotFoundError as e:
    print(f"Patient not found: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Details: {e.details}")

except ValidationError as e:
    print(f"Invalid input: {e}")

except SchemaValidationError as e:
    print(f"Response schema mismatch: {e}")
    print(f"Missing fields: {e.details['missing_fields']}")

except ABDMError as e:
    print(f"ABDM error: {e}")
```

## ⚙️ Configuration

### Initialize with Custom Settings

```python
client = ABDMClient(
    base_url="http://localhost:8090",
    client_id="your-client-id",
    client_secret="your-client-secret",
    timeout=30,                           # Request timeout (seconds)
    validate_schemas=True,                # Enable schema validation
    schema_path="/path/to/gateway.yaml"  # Custom schema path
)
```

### Auto Schema Detection

The client automatically searches for `gateway.yaml` in:
1. `../../../api-schemas/gateway.yaml` (relative to SDK)
2. `api-schemas/gateway.yaml` (current working directory)
3. `gateway.yaml` (current working directory)

### Disable Validation (Not Recommended)

```python
client = ABDMClient(
    base_url="http://localhost:8090",
    validate_schemas=False  # Skip validation (use for debugging only)
)
```

## 🧪 Running Examples

```bash
cd sdk/python/examples

# Patient discovery
python 01_patient_discovery.py

# Care context linking (interactive - requires OTP)
python 02_care_context_linking.py

# Complete consent flow
python 03_full_consent_flow.py
```

## 📖 API Reference

### ABDMClient

Main client class with high-level methods.

#### Methods

##### `discover_patient()`
Discover patient by ABHA, mobile, or demographics.

**Parameters:**
- `abha_number` (str, optional): Patient ABHA number
- `mobile` (str, optional): Mobile number
- `name` (str, optional): Patient name
- `gender` (str, optional): M, F, O, or U
- `year_of_birth` (int, optional): Birth year
- `timeout` (int): Callback timeout in seconds (default: 60)

**Returns:** `Dict[str, Any]` - Discovery result with patient and care contexts

**Raises:** `PatientNotFoundError`, `ValidationError`

---

##### `initiate_linking()`
Initiate care context linking (generates OTP).

**Parameters:**
- `patient_ref` (str): Patient reference at HIP
- `care_contexts` (List[str]): Care context IDs to link
- `timeout` (int): Callback timeout (default: 60)

**Returns:** `Dict[str, Any]` - Link reference and OTP details

**Raises:** `LinkingError`, `ValidationError`

---

##### `confirm_linking()`
Confirm linking with OTP.

**Parameters:**
- `link_ref` (str): Link reference from `initiate_linking()`
- `otp` (str): OTP received by patient
- `timeout` (int): Callback timeout (default: 60)

**Returns:** `Dict[str, Any]` - Linked patient details

**Raises:** `LinkingError`

---

##### `request_consent()`
Request patient consent for health information access.

**Parameters:**
- `patient_abha` (str): Patient ABHA with @sbx
- `purpose` (str): Purpose code (CAREMGT, BTG, etc.)
- `hi_types` (List[str]): HI types to access
- `date_from` (datetime, optional): Data from date
- `date_to` (datetime, optional): Data to date
- `data_erase_at` (datetime, optional): Data erasure date
- `requester_name` (str): Requester name
- `requester_id` (str): Requester registration ID
- `timeout` (int): Callback timeout (default: 60)

**Returns:** `Dict[str, Any]` - Consent request details

**Raises:** `ConsentError`, `ValidationError`

---

##### `fetch_health_information()`
Fetch health information after consent granted.

**Parameters:**
- `consent_id` (str): Consent artefact ID
- `data_push_url` (str): URL for HIP to push data
- `encryption_public_key` (str): Public key (base64)
- `timeout` (int): Callback timeout (default: 120)

**Returns:** `Dict[str, Any]` - HI request acknowledgement

**Raises:** `ConsentError`

## 🔧 Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black abdm_client/

# Type checking
mypy abdm_client/

# Linting
ruff check abdm_client/
```

## 📝 Changelog

### v1.0.0 (2026-02-14)

**✅ 100% ABDM Schema Compliance**

- ✅ Built-in schema validation against official ABDM gateway.yaml
- ✅ All latest schema fixes included:
  - Requester.identifier is object (not string)
  - UsePurpose.code is string (not enum)
  - HIType is string (not enum)
  - No extra fields (OrganizationRepresentation.name removed)
- ✅ Automatic validation of:
  - Purpose codes (CAREMGT, BTG, PUBHLTH, etc.)
  - HI types (DiagnosticReport, Prescription, etc.)
  - ABHA number format
  - Date ranges
  - Required fields
- ✅ Comprehensive error handling with custom exceptions
- ✅ Full async/await support
- ✅ Type-safe with Pydantic
- ✅ Production-ready with timeout handling
- ✅ Example scripts for all workflows

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📞 Support

- **Documentation**: Check examples/ directory
- **Issues**: Report at GitHub Issues
- **ABDM Documentation**: https://sandbox.abdm.gov.in/docs

## ⭐ Related Projects

- [ABDM Local Dev Kit](../../README.md) - Complete ABDM development environment
- [ABDM Official Sandbox](https://sandbox.abdm.gov.in) - Official ABDM sandbox

---

**Built with ❤️ for the ABDM developer community**

**✅ 100% Schema Compliant | ✅ Production Ready | ✅ Fully Validated**
