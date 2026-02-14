"""
ABDM Client Exceptions

All custom exceptions raised by the ABDM client library.
"""


class ABDMError(Exception):
    """Base exception for all ABDM client errors."""

    def __init__(self, message: str, error_code: int = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ValidationError(ABDMError):
    """Raised when input validation fails."""
    pass


class SchemaValidationError(ABDMError):
    """Raised when response doesn't match ABDM schema."""
    pass


class AuthenticationError(ABDMError):
    """Raised when authentication fails."""
    pass


class PatientNotFoundError(ABDMError):
    """Raised when patient discovery finds no matches."""
    pass


class ConsentError(ABDMError):
    """Raised when consent operations fail."""
    pass


class LinkingError(ABDMError):
    """Raised when care context linking fails."""
    pass


class TimeoutError(ABDMError):
    """Raised when operation times out."""
    pass


class NetworkError(ABDMError):
    """Raised when network communication fails."""
    pass
