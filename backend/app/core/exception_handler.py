"""
Global exception handler for the application.
Converts exceptions to standardized error responses with severity levels.
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.errors import AppError, ErrorSeverity, InternalServerError

logger = logging.getLogger(__name__)


class ErrorResponse:
    """Standardized error response format"""
    def __init__(
        self,
        detail: str,
        status_code: int,
        severity: ErrorSeverity = ErrorSeverity.CRITICAL,
        error_code: str = "UNKNOWN_ERROR",
    ):
        self.detail = detail
        self.status_code = status_code
        self.severity = severity
        self.error_code = error_code

    def to_dict(self) -> dict:
        return {
            "detail": self.detail,
            "status_code": self.status_code,
            "severity": self.severity,
            "error_code": self.error_code,
        }


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle AppError exceptions"""
    # Log based on severity
    if exc.severity == ErrorSeverity.CRITICAL:
        logger.warning(f"Critical error: {exc.detail} (code: {exc.error_code})")
    elif exc.severity == ErrorSeverity.WARNING:
        logger.info(f"Warning: {exc.detail} (code: {exc.error_code})")
    else:
        logger.debug(f"Info/Silent: {exc.detail} (code: {exc.error_code})")

    response = ErrorResponse(
        detail=exc.detail,
        status_code=exc.status_code,
        severity=exc.severity,
        error_code=exc.error_code or "UNKNOWN_ERROR",
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=response.to_dict(),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    # Extract first validation error
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field = ".".join(str(x) for x in first_error["loc"][1:])
        msg = first_error["msg"]
        detail = f"Validation error in {field}: {msg}"
    else:
        detail = "Validation error"

    logger.warning(f"Validation error: {detail}")

    response = ErrorResponse(
        detail=detail,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        severity=ErrorSeverity.CRITICAL,
        error_code="VALIDATION_ERROR",
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.to_dict(),
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)

    response = ErrorResponse(
        detail="An unexpected error occurred. Please try again later.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        severity=ErrorSeverity.SILENT,
        error_code="INTERNAL_ERROR",
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.to_dict(),
    )
