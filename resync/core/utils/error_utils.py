"""Error response utilities for standardized error handling."""

import logging
import traceback
import uuid
from typing import Any, Dict, List, Optional, Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from resync.core.logger import log_with_correlation
from resync.models.error_models import (
    AuthenticationErrorResponse,
    AuthorizationErrorResponse,
    BaseErrorResponse,
    BusinessLogicErrorResponse,
    ErrorCategory,
    ErrorSeverity,
    ExternalServiceErrorResponse,
    RateLimitErrorResponse,
    SystemErrorResponse,
    ValidationErrorResponse,
)
from resync.settings import settings

logger = logging.getLogger(__name__)


class ErrorResponseBuilder:
    """Builder class for creating standardized error responses."""

    def __init__(self):
        self._correlation_id: Optional[str] = None
        self._path: Optional[str] = None
        self._method: Optional[str] = None
        self._include_stack_trace: bool = False

    def with_correlation_id(self, correlation_id: str) -> "ErrorResponseBuilder":
        """Set the correlation ID for error tracking."""
        self._correlation_id = correlation_id
        return self

    def with_request_context(self, request: Request) -> "ErrorResponseBuilder":
        """Set request context information."""
        self._path = request.url.path
        self._method = request.method
        return self

    def with_stack_trace(self, include: bool = True) -> "ErrorResponseBuilder":
        """Set whether to include stack traces in error responses."""
        self._include_stack_trace = include
        return self

    def build_validation_error(self, validation_errors: List[Dict[str, Any]], message: Optional[str] = None) -> ValidationErrorResponse:
        """Build validation error response."""
        response = ValidationErrorResponse.from_pydantic_errors(
            validation_errors,
            correlation_id=self._correlation_id,
            path=self._path,
            method=self._method
        )
        if message:
            response.message = message
        return response

    def build_authentication_error(self, error_type: str, **kwargs) -> AuthenticationErrorResponse:
        """Build authentication error response."""
        if error_type == "unauthorized":
            return AuthenticationErrorResponse.unauthorized(
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        elif error_type == "invalid_credentials":
            return AuthenticationErrorResponse.invalid_credentials(
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        elif error_type == "token_expired":
            return AuthenticationErrorResponse.token_expired(
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        else:
            return AuthenticationErrorResponse(
                error_code="AUTHENTICATION_ERROR",
                message="Authentication failed",
                category=ErrorCategory.AUTHENTICATION,
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )

    def build_authorization_error(self, error_type: str, **kwargs) -> AuthorizationErrorResponse:
        """Build authorization error response."""
        if error_type == "forbidden":
            return AuthorizationErrorResponse.forbidden(
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        else:
            return AuthorizationErrorResponse.insufficient_permissions(
                resource=kwargs.pop("resource", "resource"),
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )

    def build_business_logic_error(self, error_type: str, **kwargs) -> BusinessLogicErrorResponse:
        """Build business logic error response."""
        if error_type == "resource_not_found":
            return BusinessLogicErrorResponse.resource_not_found(
                resource=kwargs.pop("resource", "Resource"),
                identifier=kwargs.pop("identifier", None),
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        elif error_type == "resource_already_exists":
            return BusinessLogicErrorResponse.resource_already_exists(
                resource=kwargs.pop("resource", "Resource"),
                identifier=kwargs.pop("identifier", None),
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        elif error_type == "invalid_operation":
            return BusinessLogicErrorResponse.invalid_operation(
                operation=kwargs.pop("operation", "operation"),
                reason=kwargs.pop("reason", None),
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        else:
            return BusinessLogicErrorResponse(
                error_code="BUSINESS_LOGIC_ERROR",
                message="Business logic error occurred",
                category=ErrorCategory.BUSINESS_LOGIC,
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )

    def build_system_error(self, error_type: str, exception: Optional[Exception] = None, **kwargs) -> SystemErrorResponse:
        """Build system error response."""
        if self._include_stack_trace and exception:
            kwargs["details"] = kwargs.get("details", {})
            kwargs["details"]["stack_trace"] = traceback.format_exc()

        if error_type == "internal_server_error":
            return SystemErrorResponse.internal_server_error(
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        elif error_type == "service_unavailable":
            return SystemErrorResponse.service_unavailable(
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        elif error_type == "database_error":
            return SystemErrorResponse.database_error(
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        else:
            return SystemErrorResponse(
                error_code="SYSTEM_ERROR",
                message="System error occurred",
                category=ErrorCategory.SYSTEM,
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )

    def build_external_service_error(self, service: str, error_type: str = "service_error", **kwargs) -> ExternalServiceErrorResponse:
        """Build external service error response."""
        if error_type == "timeout":
            return ExternalServiceErrorResponse.timeout(
                service=service,
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )
        else:
            return ExternalServiceErrorResponse.service_error(
                service=service,
                correlation_id=self._correlation_id,
                path=self._path,
                method=self._method,
                **kwargs
            )

    def build_rate_limit_error(self, limit: int, window: Optional[str] = None, **kwargs) -> RateLimitErrorResponse:
        """Build rate limit error response."""
        return RateLimitErrorResponse.rate_limit_exceeded(
            limit=limit,
            window=window,
            correlation_id=self._correlation_id,
            path=self._path,
            method=self._method,
            **kwargs
        )


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for error tracking."""
    return str(uuid.uuid4())


def extract_validation_errors(validation_error: Union[RequestValidationError, ValidationError]) -> List[Dict[str, Any]]:
    """Extract validation error details from FastAPI or Pydantic validation errors."""
    errors = []

    if isinstance(validation_error, RequestValidationError):
        for error in validation_error.errors():
            errors.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })
    elif isinstance(validation_error, ValidationError):
        for error in validation_error.errors():
            errors.append({
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"],
                "input": error.get("input")
            })

    return errors


def should_include_stack_trace() -> bool:
    """Determine if stack traces should be included in error responses."""
    # In development environment, include stack traces for debugging
    if hasattr(settings, 'APP_ENV') and settings.APP_ENV == 'development':
        return True

    # Check specific error detail level setting
    if hasattr(settings, 'ERROR_DETAIL_LEVEL'):
        return settings.ERROR_DETAIL_LEVEL == 'detailed'

    # Default to not including stack traces in production
    return False


def get_error_status_code(error_category: ErrorCategory) -> int:
    """Get HTTP status code based on error category."""
    status_code_map = {
        ErrorCategory.VALIDATION: status.HTTP_400_BAD_REQUEST,
        ErrorCategory.AUTHENTICATION: status.HTTP_401_UNAUTHORIZED,
        ErrorCategory.AUTHORIZATION: status.HTTP_403_FORBIDDEN,
        ErrorCategory.BUSINESS_LOGIC: status.HTTP_400_BAD_REQUEST,
        ErrorCategory.SYSTEM: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCategory.EXTERNAL_SERVICE: status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCategory.RATE_LIMIT: status.HTTP_429_TOO_MANY_REQUESTS,
    }
    return status_code_map.get(error_category, status.HTTP_500_INTERNAL_SERVER_ERROR)


def log_error_response(error_response: BaseErrorResponse, original_exception: Optional[Exception] = None) -> None:
    """Log error response with appropriate level based on severity."""
    log_data = {
        "error_code": error_response.error_code,
        "message": error_response.message,
        "category": error_response.category,
        "severity": error_response.severity,
        "correlation_id": error_response.correlation_id,
        "path": error_response.path,
        "method": error_response.method,
    }

    if original_exception:
        log_data["exception_type"] = type(original_exception).__name__

    # Log based on severity
    if error_response.severity == ErrorSeverity.CRITICAL:
        logger.critical(f"Critical error occurred: {log_data}", exc_info=original_exception if should_include_stack_trace() else None)
    elif error_response.severity == ErrorSeverity.HIGH:
        logger.error(f"High severity error occurred: {log_data}", exc_info=original_exception if should_include_stack_trace() else None)
    elif error_response.severity == ErrorSeverity.MEDIUM:
        logger.warning(f"Medium severity error occurred: {log_data}")
    else:
        logger.info(f"Low severity error occurred: {log_data}")


def create_error_response_from_exception(
    exception: Exception,
    request: Optional[Request] = None,
    correlation_id: Optional[str] = None
) -> BaseErrorResponse:
    """Create standardized error response from any exception with security considerations."""
    from resync.core.exceptions_enhanced import (
        ResyncException as EnhancedResyncException,
        DatabaseError as EnhancedDatabaseError,
        LLMError as EnhancedLLMError,
        NotFoundError as EnhancedNotFoundError,
        TWSConnectionError as EnhancedTWSConnectionError,
    )
    
    from resync.core.exceptions import (
        DatabaseError,
        LLMError,
        NotFoundError,
        ResyncException as BaseResyncException,
        TWSConnectionError,
    )

    builder = ErrorResponseBuilder()

    if correlation_id:
        builder.with_correlation_id(correlation_id)
    else:
        builder.with_correlation_id(generate_correlation_id())

    if request:
        builder.with_request_context(request)

    # Enhanced security: only include stack traces in non-production environments
    is_production = getattr(settings, 'APP_ENV', 'development') == 'production'
    include_stack_trace = should_include_stack_trace() and not is_production
    
    # In production, sanitize error messages to prevent information disclosure
    if is_production:
        # Don't include raw exception details in production
        builder.with_stack_trace(include_stack_trace and is_production is False)
    else:
        builder.with_stack_trace(include_stack_trace)

    # Handle enhanced Resync exceptions with richer information
    if isinstance(exception, EnhancedResyncException):
        return _handle_enhanced_resync_exception(builder, exception, is_production)
    
    # Handle base Resync exceptions for backward compatibility
    elif isinstance(exception, (TWSConnectionError, EnhancedTWSConnectionError)):
        return builder.build_external_service_error("TWS", "service_error")
    elif isinstance(exception, (LLMError, EnhancedLLMError)):
        return builder.build_external_service_error("LLM", "service_error")
    elif isinstance(exception, (DatabaseError, EnhancedDatabaseError)):
        return builder.build_system_error("database_error")
    elif isinstance(exception, (NotFoundError, EnhancedNotFoundError)):
        return builder.build_business_logic_error("resource_not_found", resource="Resource")
    elif isinstance(exception, BaseResyncException):
        # Generic base ResyncException - create system error
        return builder.build_system_error("internal_server_error", exception=exception if not is_production else None)
    else:
        # Unknown exception - create system error
        return builder.build_system_error("internal_server_error", exception=exception if not is_production else None)


def _handle_enhanced_resync_exception(builder: ErrorResponseBuilder, exception: Exception, is_production: bool) -> BaseErrorResponse:
    """Handle enhanced Resync exceptions with rich information."""
    # Use the enhanced exception's information to create a more detailed response
    message = exception.message
    user_friendly_message = exception.user_friendly_message
    details = exception.details.copy()  # Copy to avoid modifying original
    
    # Sanitize details in production to prevent sensitive data leakage
    if is_production:
        # Remove potentially sensitive information
        details.pop('original_exception', None)
        if 'details' in details:
            # Further sanitize nested details
            if isinstance(details['details'], dict):
                details['details'] = {k: v for k, v in details['details'].items() 
                                    if k not in ['password', 'token', 'credentials', 'key']}
    
    # Map the enhanced exception to the appropriate response type based on category
    if exception.error_category == "VALIDATION":
        return builder.build_validation_error(
            [{"loc": ["validation"], "msg": sanitize_error_message(message), "type": "value_error"}], 
            sanitize_error_message(user_friendly_message)
        )
    elif exception.error_category == "BUSINESS_LOGIC":
        return _handle_business_logic_exception(builder, exception, message, user_friendly_message, details, is_production)
    elif exception.error_category == "EXTERNAL_SERVICE":
        service_name = details.get("service", "External Service") if details else "External Service"
        return builder.build_external_service_error(
            service_name,
            user_friendly_message=sanitize_error_message(user_friendly_message),
            details=details
        )
    elif exception.error_category == "SYSTEM":
        return builder.build_system_error(
            "internal_server_error", 
            user_friendly_message=sanitize_error_message(user_friendly_message),
            details=details,
            exception=exception if not is_production else None
        )
    else:
        # For other enhanced exceptions
        return builder.build_system_error(
            "internal_server_error", 
            exception=exception if not is_production else None,
            user_friendly_message=sanitize_error_message(user_friendly_message),
            details=details
        )


def _handle_business_logic_exception(builder: ErrorResponseBuilder, exception: Exception, message: str, 
                                   user_friendly_message: str, details: dict, is_production: bool) -> BaseErrorResponse:
    """Handle business logic exceptions."""
    from resync.core.exceptions_enhanced import NotFoundError as EnhancedNotFoundError
    
    if isinstance(exception, EnhancedNotFoundError):
        return builder.build_business_logic_error(
            "resource_not_found", 
            resource="Resource",
            user_friendly_message=sanitize_error_message(user_friendly_message),
            details=details
        )
    else:
        return builder.build_business_logic_error(
            "invalid_operation",
            user_friendly_message=sanitize_error_message(user_friendly_message),
            details=details
        )


def sanitize_error_message(message: str) -> str:
    """
    Sanitize error messages to prevent sensitive information disclosure.
    """
    if not message:
        return "An error occurred"
    
    # Replace potentially sensitive information
    sanitized = message
    sensitive_patterns = [
        r'password\s*[:=]\s*[\w\d!@#$%^&*()]+',
        r'token\s*[:=]\s*[A-Za-z0-9_\-\.]+',
        r'key\s*[:=]\s*[A-Za-z0-9_\-]+',
        r'api_key\s*[:=]\s*[A-Za-z0-9_\-]+',
        r'credential\s*[:=]\s*[^\s,;]+',
        r'connection_string[:=]\s*[^\s,;]+'
    ]
    
    import re
    for pattern in sensitive_patterns:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
    
    return sanitized


def create_json_response_from_error(error_response: BaseErrorResponse) -> JSONResponse:
    """Create FastAPI JSONResponse from standardized error response."""
    status_code = get_error_status_code(error_response.category)
    content = error_response.dict(exclude_none=True)

    return JSONResponse(
        status_code=status_code,
        content=content
    )


def register_exception_handlers(app):
    """Register standardized exception handlers for the FastAPI application."""
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from resync.core.exceptions import ResyncException as BaseResyncException
    from resync.core.exceptions_enhanced import ResyncException as EnhancedResyncException

    # Register handler for validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        correlation_id = generate_correlation_id()
        error_response = ErrorResponseBuilder() \
            .with_correlation_id(correlation_id) \
            .with_request_context(request) \
            .build_validation_error(extract_validation_errors(exc))

        log_error_response(error_response, exc)

        return create_json_response_from_error(error_response)

    # Register handler for standard HTTP exceptions
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        correlation_id = generate_correlation_id()
        builder = ErrorResponseBuilder().with_correlation_id(correlation_id).with_request_context(request)

        # Map HTTP status codes to appropriate error types
        if exc.status_code == 404:
            error_response = builder.build_business_logic_error(
                "resource_not_found", 
                resource="Resource"
            )
        elif exc.status_code == 401:
            error_response = builder.build_authentication_error("unauthorized")
        elif exc.status_code == 403:
            error_response = builder.build_authorization_error("forbidden")
        elif exc.status_code == 429:
            error_response = builder.build_rate_limit_error(
                limit=getattr(request.state, 'rate_limit', {}).get('limit', 0)
            )
        else:
            error_response = builder.build_system_error("internal_server_error")

        error_response.error_code = f"HTTP_{exc.status_code}"
        error_response.message = exc.detail if exc.detail else f"HTTP Error {exc.status_code}"

        log_error_response(error_response)

        return create_json_response_from_error(error_response)

    # Register handler for enhanced Resync custom exceptions first
    @app.exception_handler(EnhancedResyncException)
    async def enhanced_resync_exception_handler(request: Request, exc: EnhancedResyncException):
        correlation_id = generate_correlation_id()
        error_response = create_error_response_from_exception(exc, request, correlation_id)

        log_error_response(error_response, exc)

        return create_json_response_from_error(error_response)

    # Register handler for base Resync custom exceptions
    @app.exception_handler(BaseResyncException)
    async def base_resync_exception_handler(request: Request, exc: BaseResyncException):
        correlation_id = generate_correlation_id()
        error_response = create_error_response_from_exception(exc, request, correlation_id)

        log_error_response(error_response, exc)

        return create_json_response_from_error(error_response)

    return app
