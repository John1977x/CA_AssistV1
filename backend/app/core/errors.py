"""
Error handling and categorization for the application.
Classifies errors into severity levels for frontend display.
"""

from enum import Enum
from typing import Optional, Any
from fastapi import HTTPException, status


class ErrorSeverity(str, Enum):
    """Error severity levels for frontend display"""
    CRITICAL = "critical"      # Must show to user (auth, validation, business logic)
    WARNING = "warning"        # Should show to user (conflicts, limits)
    INFO = "info"              # Optional info (not found, already exists)
    SILENT = "silent"          # Don't show to user (internal errors, retryable)


class AppError(HTTPException):
    """
    Application error with severity level.
    Frontend will only show CRITICAL and WARNING errors as popups.
    """
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
        error_code: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.severity = severity
        self.error_code = error_code


# ─── Error Categories ────────────────────────────────────────────────────────

class AuthenticationError(AppError):
    """Authentication failures - show to user"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            severity=ErrorSeverity.CRITICAL,
            error_code="AUTH_FAILED"
        )


class AuthorizationError(AppError):
    """Authorization failures - show to user"""
    def __init__(self, detail: str = "You don't have permission to perform this action"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            severity=ErrorSeverity.CRITICAL,
            error_code="AUTH_DENIED"
        )


class ValidationError(AppError):
    """Validation errors - show to user"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            severity=ErrorSeverity.CRITICAL,
            error_code="VALIDATION_ERROR"
        )


class ResourceNotFoundError(AppError):
    """Resource not found - don't show (silent)"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            detail=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            severity=ErrorSeverity.SILENT,
            error_code="NOT_FOUND"
        )


class ConflictError(AppError):
    """Resource conflict - show to user"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            severity=ErrorSeverity.WARNING,
            error_code="CONFLICT"
        )


class LimitExceededError(AppError):
    """Limit exceeded - show to user"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            severity=ErrorSeverity.WARNING,
            error_code="LIMIT_EXCEEDED"
        )


class BusinessLogicError(AppError):
    """Business logic violation - show to user"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
            severity=ErrorSeverity.CRITICAL,
            error_code="BUSINESS_LOGIC_ERROR"
        )


class InternalServerError(AppError):
    """Internal server error - don't show (silent)"""
    def __init__(self, detail: str = "An internal error occurred"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            severity=ErrorSeverity.SILENT,
            error_code="INTERNAL_ERROR"
        )


class ExternalServiceError(AppError):
    """External service error (Stripe, email, etc) - show to user"""
    def __init__(self, service: str, detail: str):
        super().__init__(
            detail=f"{service} error: {detail}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            severity=ErrorSeverity.WARNING,
            error_code="EXTERNAL_SERVICE_ERROR"
        )
