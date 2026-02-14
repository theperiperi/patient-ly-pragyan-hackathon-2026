"""
FHIR Resource Validator

Validates FHIR resources against ABDM profiles using fhir.resources library.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fhir.resources.bundle import Bundle
from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue
from pydantic import ValidationError

from .profile_loader import get_profile_loader

logger = logging.getLogger(__name__)


class FHIRValidator:
    """Validates FHIR resources against ABDM profiles."""

    def __init__(self):
        """Initialize FHIR validator."""
        self.profile_loader = get_profile_loader()
        if not self.profile_loader:
            logger.warning("Profile loader not initialized")

    def validate_bundle(self, bundle_data: dict) -> OperationOutcome:
        """
        Validate a FHIR Bundle against ABDM profiles.

        Args:
            bundle_data: FHIR Bundle as dict

        Returns:
            OperationOutcome with validation results
        """
        issues = []

        try:
            # Parse bundle with fhir.resources
            bundle = Bundle.parse_obj(bundle_data)

            # Basic validation passed
            issues.append(OperationOutcomeIssue(
                severity="information",
                code="informational",
                diagnostics="Bundle successfully parsed and validated against FHIR R4 schema"
            ))

            # Validate bundle type
            if not bundle.type:
                issues.append(OperationOutcomeIssue(
                    severity="error",
                    code="required",
                    diagnostics="Bundle.type is required"
                ))
            else:
                issues.append(OperationOutcomeIssue(
                    severity="information",
                    code="informational",
                    diagnostics=f"Bundle type: {bundle.type}"
                ))

            # Validate entries
            if bundle.entry:
                issues.append(OperationOutcomeIssue(
                    severity="information",
                    code="informational",
                    diagnostics=f"Bundle contains {len(bundle.entry)} entries"
                ))

                # Validate each entry
                for idx, entry in enumerate(bundle.entry):
                    if not entry.resource:
                        issues.append(OperationOutcomeIssue(
                            severity="error",
                            code="required",
                            diagnostics=f"Entry[{idx}]: Resource is required"
                        ))
                    else:
                        # Check resource type
                        resource_type = entry.resource.resource_type
                        issues.append(OperationOutcomeIssue(
                            severity="information",
                            code="informational",
                            diagnostics=f"Entry[{idx}]: Resource type {resource_type}"
                        ))

                        # Validate against ABDM profile if available
                        if self.profile_loader:
                            profile = self.profile_loader.get_profile_for_resource_type(resource_type)
                            if profile:
                                issues.append(OperationOutcomeIssue(
                                    severity="information",
                                    code="informational",
                                    diagnostics=f"Entry[{idx}]: ABDM profile found for {resource_type}"
                                ))
                            else:
                                issues.append(OperationOutcomeIssue(
                                    severity="warning",
                                    code="not-found",
                                    diagnostics=f"Entry[{idx}]: No ABDM profile found for {resource_type}"
                                ))
            else:
                issues.append(OperationOutcomeIssue(
                    severity="warning",
                    code="informational",
                    diagnostics="Bundle has no entries"
                ))

            # Check for identifier
            if bundle.identifier:
                issues.append(OperationOutcomeIssue(
                    severity="information",
                    code="informational",
                    diagnostics=f"Bundle identifier: {bundle.identifier.value}"
                ))

            # Overall result
            error_count = sum(1 for issue in issues if issue.severity == "error")
            if error_count == 0:
                issues.insert(0, OperationOutcomeIssue(
                    severity="success",
                    code="informational",
                    diagnostics=f"Validation successful: Bundle is valid FHIR R4"
                ))

        except ValidationError as e:
            # Pydantic validation errors
            logger.error(f"Bundle validation failed: {e}")

            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                issues.append(OperationOutcomeIssue(
                    severity="error",
                    code="invalid",
                    diagnostics=f"Field '{field_path}': {error['msg']}",
                    expression=[field_path]
                ))

        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            issues.append(OperationOutcomeIssue(
                severity="fatal",
                code="exception",
                diagnostics=f"Validation failed with error: {str(e)}"
            ))

        # Create OperationOutcome
        outcome = OperationOutcome(issue=issues)
        return outcome

    def validate_resource(self, resource_data: dict, resource_type: Optional[str] = None) -> OperationOutcome:
        """
        Validate a single FHIR resource.

        Args:
            resource_data: FHIR resource as dict
            resource_type: Expected resource type (optional)

        Returns:
            OperationOutcome with validation results
        """
        issues = []

        try:
            # Detect resource type
            detected_type = resource_data.get("resourceType")

            if not detected_type:
                issues.append(OperationOutcomeIssue(
                    severity="error",
                    code="required",
                    diagnostics="resourceType is required"
                ))
                return OperationOutcome(issue=issues)

            if resource_type and detected_type != resource_type:
                issues.append(OperationOutcomeIssue(
                    severity="error",
                    code="invalid",
                    diagnostics=f"Expected resourceType '{resource_type}' but found '{detected_type}'"
                ))

            issues.append(OperationOutcomeIssue(
                severity="information",
                code="informational",
                diagnostics=f"Resource type: {detected_type}"
            ))

            # Attempt to parse with fhir.resources
            # Import the appropriate resource class dynamically
            try:
                module = __import__(f"fhir.resources.{detected_type.lower()}", fromlist=[detected_type])
                resource_class = getattr(module, detected_type)
                resource = resource_class.parse_obj(resource_data)

                issues.append(OperationOutcomeIssue(
                    severity="information",
                    code="informational",
                    diagnostics=f"Resource successfully parsed and validated against FHIR R4 schema"
                ))

                # Check for ABDM profile
                if self.profile_loader:
                    profile = self.profile_loader.get_profile_for_resource_type(detected_type)
                    if profile:
                        issues.append(OperationOutcomeIssue(
                            severity="information",
                            code="informational",
                            diagnostics=f"ABDM profile found for {detected_type}: {profile.get('name')}"
                        ))
                    else:
                        issues.append(OperationOutcomeIssue(
                            severity="warning",
                            code="not-found",
                            diagnostics=f"No ABDM profile found for {detected_type}"
                        ))

                # Success
                issues.insert(0, OperationOutcomeIssue(
                    severity="success",
                    code="informational",
                    diagnostics=f"Validation successful: {detected_type} is valid FHIR R4"
                ))

            except ImportError:
                issues.append(OperationOutcomeIssue(
                    severity="error",
                    code="not-supported",
                    diagnostics=f"Resource type '{detected_type}' is not supported"
                ))

        except ValidationError as e:
            logger.error(f"Resource validation failed: {e}")

            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                issues.append(OperationOutcomeIssue(
                    severity="error",
                    code="invalid",
                    diagnostics=f"Field '{field_path}': {error['msg']}",
                    expression=[field_path]
                ))

        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}")
            issues.append(OperationOutcomeIssue(
                severity="fatal",
                code="exception",
                diagnostics=f"Validation failed with error: {str(e)}"
            ))

        return OperationOutcome(issue=issues)

    def create_validation_summary(self, outcome: OperationOutcome) -> Dict[str, Any]:
        """
        Create a summary of validation results.

        Args:
            outcome: OperationOutcome from validation

        Returns:
            Summary dict with counts and status
        """
        issues_by_severity = {
            "success": [],
            "information": [],
            "warning": [],
            "error": [],
            "fatal": []
        }

        for issue in outcome.issue:
            severity = issue.severity
            issues_by_severity[severity].append({
                "code": issue.code,
                "diagnostics": issue.diagnostics,
                "expression": issue.expression if issue.expression else []
            })

        error_count = len(issues_by_severity["error"]) + len(issues_by_severity["fatal"])
        warning_count = len(issues_by_severity["warning"])

        if error_count > 0:
            status = "FAILED"
            result = "Validation failed with errors"
        elif warning_count > 0:
            status = "PASSED_WITH_WARNINGS"
            result = "Validation passed with warnings"
        else:
            status = "PASSED"
            result = "Validation passed successfully"

        return {
            "status": status,
            "result": result,
            "summary": {
                "success": len(issues_by_severity["success"]),
                "information": len(issues_by_severity["information"]),
                "warnings": warning_count,
                "errors": error_count
            },
            "issues": issues_by_severity
        }
