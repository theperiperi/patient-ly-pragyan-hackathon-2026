# Automated Schema Compliance Testing

## Overview

This test suite programmatically validates that all implemented Pydantic models and API endpoints match the official ABDM API specifications with 100% accuracy.

## How It Works

1. **Loads Official Schemas**: Reads `api-schemas/gateway.yaml` (official ABDM spec)
2. **Validates Models**: Compares Pydantic model definitions against schema
3. **Checks All Fields**: Validates field names, types, required/optional, formats
4. **Reports Violations**: Lists ALL mismatches with exact locations

## Running Tests

### Install Test Dependencies

```bash
cd tests
pip install -r requirements.txt
```

### Run Full Test Suite

```bash
# From project root
python -m pytest tests/test_schema_compliance.py -v

# Or from tests directory
cd tests
pytest test_schema_compliance.py -v
```

### Run Specific Test Classes

```bash
# Test only consent request schema
pytest tests/test_schema_compliance.py::TestConsentRequestSchema -v

# Test endpoint coverage
pytest tests/test_schema_compliance.py::TestEndpointCoverage -v

# Test data validation
pytest tests/test_schema_compliance.py::TestDataValidation -v
```

## Test Coverage

### TestConsentRequestSchema
- ✅ ConsentRequest structure matches official schema
- ✅ UsePurpose structure (code is string, not enum)
- ✅ Permission structure with all required fields
- ✅ OrganizationRepresentation (no extra 'name' field)
- ✅ Requester structure (identifier is object with type/value/system)

### TestEndpointCoverage
- ✅ All consent endpoints present in schema
- ✅ Discovery endpoints defined
- ✅ Linking endpoints defined

### TestDataValidation
- ✅ Purpose codes accept strings (not just enum values)
- ✅ HI types accept strings (not just enum values)
- ✅ ConsentRequest instantiation with valid ABDM data

## Expected Output

### All Tests Passing (100% Compliance)
```
tests/test_schema_compliance.py::TestConsentRequestSchema::test_consent_request_structure PASSED
tests/test_schema_compliance.py::TestConsentRequestSchema::test_use_purpose_structure PASSED
tests/test_schema_compliance.py::TestConsentRequestSchema::test_permission_structure PASSED
tests/test_schema_compliance.py::TestConsentRequestSchema::test_organization_representation PASSED
tests/test_schema_compliance.py::TestConsentRequestSchema::test_requester_structure PASSED
tests/test_schema_compliance.py::TestEndpointCoverage::test_consent_endpoints_exist PASSED
tests/test_schema_compliance.py::TestEndpointCoverage::test_discovery_endpoints_required PASSED
tests/test_schema_compliance.py::TestEndpointCoverage::test_linking_endpoints_required PASSED
tests/test_schema_compliance.py::TestDataValidation::test_purpose_codes_are_strings PASSED
tests/test_schema_compliance.py::TestDataValidation::test_hi_types_are_strings PASSED
tests/test_schema_compliance.py::TestDataValidation::test_consent_request_accepts_valid_data PASSED

========== 11 passed in 0.45s ==========
```

### Test Failures (Schema Violations Found)
```
FAILED tests/test_schema_compliance.py::TestConsentRequestSchema::test_requester_structure
AssertionError: Schema compliance violations found:
TYPE MISMATCH: Requester.identifier - Expected object, got <class 'str'>
REQUIRED MISMATCH: Requester.identifier.type - Required in schema but not in model
```

## Continuous Integration

### Add to GitHub Actions

```yaml
name: Schema Compliance Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd tests
          pip install -r requirements.txt
      - name: Run schema compliance tests
        run: |
          python -m pytest tests/test_schema_compliance.py -v
```

## Extending Tests

### Add New Model Validation

```python
def test_new_model_structure(self, official_schema):
    """Validate NewModel matches official schema."""
    schema_def = get_schema_definition(
        official_schema,
        "#/components/schemas/NewModel"
    )

    violations = validate_field_types(
        NewModel,
        schema_def,
        "NewModel"
    )

    assert len(violations) == 0, "\n".join([
        "NewModel schema violations:",
        *violations
    ])
```

### Add Endpoint Implementation Check

```python
def test_new_endpoint_implemented(self):
    """Verify new endpoint is implemented."""
    from services.gateway.api import new_module

    # Check endpoint exists
    assert hasattr(new_module.router, 'routes')

    # Check specific route path
    paths = [route.path for route in new_module.router.routes]
    assert "/v0.5/new-endpoint" in paths
```

## Benefits

1. **100% Schema Accuracy**: Programmatically ensures compliance
2. **Catches Regressions**: Fails if someone breaks schema compliance
3. **Fast Feedback**: Runs in <1 second
4. **CI/CD Ready**: Integrates with GitHub Actions, Jenkins, etc.
5. **Self-Documenting**: Tests serve as spec documentation

## Fixing Violations

When tests fail:

1. **Read the error message** - Shows exact field path and mismatch
2. **Check official schema** - Reference `api-schemas/gateway.yaml`
3. **Update Pydantic model** - Fix the field type/requirement
4. **Re-run tests** - Verify fix

Example fix workflow:
```bash
# Run tests to find violations
pytest tests/test_schema_compliance.py::TestConsentRequestSchema -v

# Fix the model in services/consent_manager/models/consent.py

# Re-run to verify
pytest tests/test_schema_compliance.py::TestConsentRequestSchema -v

# Should pass now
```
