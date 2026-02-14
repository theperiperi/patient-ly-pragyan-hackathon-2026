# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-14

### Added
- Initial release of ABDM Python Client Library
- 100% ABDM Schema Compliance with automatic validation
- Built-in schema validation against official ABDM OpenAPI specification
- Support for all major ABDM workflows:
  - Patient Discovery (by ABHA, mobile, or demographics)
  - Care Context Linking (with OTP verification)
  - Consent Management (request, approve, revoke)
  - Health Information Exchange (fetch and decrypt)
- HIP Callback Support:
  - All 8 ABDM callback endpoints implemented
  - Add care contexts to existing links
  - Notify HIU about new health records
  - Response builders for HIP implementations
- Comprehensive error handling with custom exceptions:
  - `ABDMError` - Base exception
  - `ValidationError` - Input validation failures
  - `SchemaValidationError` - Response schema mismatches
  - `AuthenticationError` - Auth failures
  - `PatientNotFoundError` - Patient not found
  - `ConsentError` - Consent operation failures
  - `LinkingError` - Linking failures
- Full async/await support with httpx
- Type-safe implementation with Pydantic validation
- Automatic schema detection and loading
- Production-ready timeout handling
- Complete example scripts for all workflows
- Comprehensive API documentation

### Fixed
- Requester.identifier is now object type (not string)
- UsePurpose.code is now string type (not enum)
- HIType is now string type (not enum)
- Removed extra OrganizationRepresentation.name field
- Proper ABHA number format validation
- Date range consistency checks

### Security
- MIT License applied
- No hardcoded credentials
- Secure async HTTP client implementation

[1.0.0]: https://github.com/ABDM/abdm-client-python/releases/tag/v1.0.0
