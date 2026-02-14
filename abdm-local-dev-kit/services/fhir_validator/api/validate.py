"""
FHIR Validation API

Endpoints for validating FHIR resources against ABDM profiles.
"""

import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Body, Query, HTTPException
from pydantic import BaseModel, Field

from utils.validator import FHIRValidator
from utils.profile_loader import get_profile_loader

logger = logging.getLogger(__name__)
router = APIRouter(tags=["FHIR Validation"])


# ============================================================================
# Pydantic Models
# ============================================================================

class ValidationRequest(BaseModel):
    """Request to validate a FHIR resource."""
    resource: dict = Field(..., description="FHIR resource to validate (Bundle or any resource)")
    resourceType: Optional[str] = Field(None, description="Expected resource type (optional)")
    strict: bool = Field(False, description="Enable strict validation mode")

class ValidationResponse(BaseModel):
    """Response from FHIR validation."""
    valid: bool = Field(..., description="Whether validation passed")
    status: str = Field(..., description="Validation status (PASSED, PASSED_WITH_WARNINGS, FAILED)")
    operationOutcome: dict = Field(..., description="FHIR OperationOutcome with detailed results")
    summary: dict = Field(..., description="Summary of validation issues")


class ProfileInfo(BaseModel):
    """FHIR profile information."""
    name: str = Field(..., example="Patient")
    id: str = Field(..., example="Patient")
    url: str = Field(..., example="https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient")
    type: str = Field(..., example="Patient")
    version: str = Field(..., example="1.0.0")
    description: str = Field(..., example="ABDM profile for Patient resource")


class ProfilesListResponse(BaseModel):
    """Response listing available FHIR profiles."""
    total: int = Field(..., description="Total number of profiles")
    profiles: list = Field(..., description="List of available profiles")


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/validate", response_model=ValidationResponse)
async def validate_fhir_resource(
    request_data: dict = Body(..., example={
        "resourceType": "Bundle",
        "type": "document",
        "entry": []
    })
):
    """
    Validate FHIR resource against ABDM profiles.

    Validates a FHIR Bundle or any FHIR resource against the official FHIR R4
    schema and ABDM-specific profiles. Returns an OperationOutcome with
    detailed validation results.

    **Supported Resource Types:**
    - Bundle (all ABDM HI types: DiagnosticReport, Prescription, DischargeSummary, etc.)
    - Patient
    - Practitioner
    - Organization
    - Observation
    - Condition
    - Medication
    - And all other FHIR R4 resources

    **Validation Levels:**
    1. **FHIR R4 Schema Validation**: Ensures resource structure matches FHIR R4 specification
    2. **ABDM Profile Validation**: Checks against ABDM-specific constraints (if profile exists)

    Args:
        request_data: FHIR resource to validate (can be any FHIR resource)

    Returns:
        ValidationResponse with OperationOutcome and summary

    Example:
        ```json
        {
            "resourceType": "Bundle",
            "type": "document",
            "identifier": {
                "system": "https://example.com",
                "value": "bundle-001"
            },
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-001",
                        "name": [{"text": "John Doe"}]
                    }
                }
            ]
        }
        ```
    """
    logger.info(f"Validating FHIR resource: type={request_data.get('resourceType')}")

    validator = FHIRValidator()

    # Detect resource type
    resource_type = request_data.get("resourceType")

    if not resource_type:
        raise HTTPException(
            status_code=400,
            detail="resourceType is required in FHIR resource"
        )

    # Validate based on resource type
    if resource_type == "Bundle":
        outcome = validator.validate_bundle(request_data)
    else:
        outcome = validator.validate_resource(request_data, resource_type)

    # Create summary
    summary_data = validator.create_validation_summary(outcome)

    # Determine if valid
    is_valid = summary_data["status"] in ["PASSED", "PASSED_WITH_WARNINGS"]

    # Convert OperationOutcome to dict
    outcome_dict = outcome.dict()

    return ValidationResponse(
        valid=is_valid,
        status=summary_data["status"],
        operationOutcome=outcome_dict,
        summary=summary_data
    )


@router.get("/profiles", response_model=ProfilesListResponse)
async def list_fhir_profiles(
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    search: Optional[str] = Query(None, description="Search in profile name/description")
):
    """
    List available ABDM FHIR profiles.

    Returns a list of all FHIR StructureDefinition profiles available for
    validation. Profiles can be filtered by resource type or searched by name.

    **Available ABDM Profiles:**
    - **Patient**: Patient demographics and identifiers
    - **Practitioner**: Healthcare provider information
    - **Organization**: Healthcare organization details
    - **Observation**: Clinical observations and vital signs
    - **DiagnosticReport**: Diagnostic test results
    - **Medication**: Medication information
    - **Prescription**: Medication prescriptions
    - **DischargeSummary**: Hospital discharge summaries
    - And 60+ more ABDM-specific profiles

    Args:
        resource_type: Filter profiles by FHIR resource type (e.g., "Patient", "Bundle")
        search: Search term to filter profiles by name or description

    Returns:
        List of available profiles with metadata

    Example Response:
        ```json
        {
            "total": 65,
            "profiles": [
                {
                    "name": "Patient",
                    "id": "Patient",
                    "url": "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient",
                    "type": "Patient",
                    "version": "1.0.0",
                    "description": "ABDM profile for Patient resource"
                }
            ]
        }
        ```
    """
    logger.info(f"Listing FHIR profiles: resourceType={resource_type}, search={search}")

    profile_loader = get_profile_loader()

    if not profile_loader:
        raise HTTPException(
            status_code=500,
            detail="Profile loader not initialized"
        )

    # Get all profiles
    profiles = profile_loader.list_profiles()

    # Filter by resource type
    if resource_type:
        profiles = [p for p in profiles if p.get("type") == resource_type]

    # Search in name/description
    if search:
        search_lower = search.lower()
        profiles = [
            p for p in profiles
            if search_lower in (p.get("name", "").lower())
            or search_lower in (p.get("description", "").lower())
        ]

    logger.info(f"Returning {len(profiles)} profiles")

    return ProfilesListResponse(
        total=len(profiles),
        profiles=profiles
    )


@router.get("/profiles/{profile_name}")
async def get_profile_details(
    profile_name: str
):
    """
    Get detailed information about a specific FHIR profile.

    Retrieves the complete StructureDefinition for the specified profile,
    including all constraints, extensions, and data elements.

    Args:
        profile_name: Profile name or ID (e.g., "Patient", "DiagnosticReportImaging")

    Returns:
        Complete StructureDefinition JSON

    Example:
        GET /profiles/Patient

    Response:
        ```json
        {
            "resourceType": "StructureDefinition",
            "id": "Patient",
            "url": "https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient",
            "name": "Patient",
            "status": "active",
            "kind": "resource",
            "abstract": false,
            "type": "Patient",
            ...
        }
        ```
    """
    logger.info(f"Get profile details: {profile_name}")

    profile_loader = get_profile_loader()

    if not profile_loader:
        raise HTTPException(
            status_code=500,
            detail="Profile loader not initialized"
        )

    profile = profile_loader.get_profile(profile_name)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=f"Profile not found: {profile_name}"
        )

    return profile


@router.post("/validate-batch")
async def validate_batch(
    resources: list = Body(..., description="List of FHIR resources to validate")
):
    """
    Validate multiple FHIR resources in batch.

    Validates multiple FHIR resources and returns aggregated results.
    Useful for validating all entries in a Bundle or multiple resources.

    Args:
        resources: List of FHIR resources to validate

    Returns:
        Batch validation results with individual outcomes

    Example Request:
        ```json
        [
            {
                "resourceType": "Patient",
                "id": "patient-001",
                "name": [{"text": "John Doe"}]
            },
            {
                "resourceType": "Observation",
                "id": "obs-001",
                "status": "final",
                "code": {"text": "Blood Pressure"}
            }
        ]
        ```
    """
    logger.info(f"Batch validation: {len(resources)} resources")

    validator = FHIRValidator()

    results = []
    overall_valid = True

    for idx, resource_data in enumerate(resources):
        resource_type = resource_data.get("resourceType", "Unknown")
        logger.debug(f"Validating resource {idx}: {resource_type}")

        try:
            if resource_type == "Bundle":
                outcome = validator.validate_bundle(resource_data)
            else:
                outcome = validator.validate_resource(resource_data, resource_type)

            summary = validator.create_validation_summary(outcome)
            is_valid = summary["status"] in ["PASSED", "PASSED_WITH_WARNINGS"]

            if not is_valid:
                overall_valid = False

            results.append({
                "index": idx,
                "resourceType": resource_type,
                "resourceId": resource_data.get("id", f"resource-{idx}"),
                "valid": is_valid,
                "status": summary["status"],
                "summary": summary["summary"],
                "operationOutcome": outcome.dict()
            })

        except Exception as e:
            logger.error(f"Error validating resource {idx}: {e}")
            overall_valid = False

            results.append({
                "index": idx,
                "resourceType": resource_type,
                "resourceId": resource_data.get("id", f"resource-{idx}"),
                "valid": False,
                "status": "ERROR",
                "error": str(e)
            })

    return {
        "total": len(resources),
        "valid": overall_valid,
        "passed": sum(1 for r in results if r.get("valid")),
        "failed": sum(1 for r in results if not r.get("valid")),
        "results": results
    }
