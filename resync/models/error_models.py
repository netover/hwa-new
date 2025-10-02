"""Standardized error response models for the FastAPI application."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class ErrorCategory(str, Enum):
    """Error category enumeration for consistent error classification."""
    VALIDATION = "VALIDATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    SYSTEM = "SYSTEM"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    RATE_LIMIT = "RATE_LIMIT"


class ErrorSeverity(str, Enum):
    """Error severity enumeration for consistent error prioritization."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    value: Optional[Any] = Field(None, description="Value that failed validation")
    location: Optional[str] = Field(None, description="Location of the field (body, query, path, header)")


class BaseErrorResponse(BaseModel):
    """Base error response model with consistent structure across all error types."""
    error_code: str = Field(..., description="Application-specific error code")
    message: str = Field(..., description="Human-readable error message")
    category: ErrorCategory = Field(..., description="Error category for classification")
    severity: ErrorSeverity = Field(ErrorSeverity.MEDIUM, description="Error severity level")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp in UTC")
    correlation_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique correlation ID for request tracking")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    user_friendly_message: Optional[str] = Field(None, description="User-friendly error message")
    troubleshooting_hints: List[str] = Field(default_factory=list, description="Helpful hints for resolving the error")
    request_context: Optional[Dict[str, Any]] = Field(None, description="Request context information")
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


class ValidationErrorResponse(BaseErrorResponse):
    """Error response model for validation errors with detailed field information."""
    category: ErrorCategory = ErrorCategory.VALIDATION
    details: List[ValidationErrorDetail] = Field(..., description="List of validation error details")
    
    @classmethod
    def from_pydantic_errors(cls, errors: List[Dict[str, Any]], correlation_id: Optional[str] = None) -> "ValidationErrorResponse":
        """Create validation error response from Pydantic validation errors."""
        details = []
        for error in errors:
            field = ".".join(str(loc) for loc in error.get("loc", []))
            details.append(ValidationErrorDetail(
                field=field,
                message=error.get("msg", "Validation failed"),
                value=error.get("input"),
                location="body"  # Default location for most validation errors
            ))
        
        return cls(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            details=details,
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.LOW,
            user_friendly_message="Please check your input and try again."
        )


class AuthenticationErrorResponse(BaseErrorResponse):
    """Error response model for authentication errors."""
    category: ErrorCategory = ErrorCategory.AUTHENTICATION
    
    @classmethod
    def unauthorized(cls, correlation_id: Optional[str] = None) -> "AuthenticationErrorResponse":
        """Create unauthorized error response."""
        return cls(
            error_code="UNAUTHORIZED",
            message="Authentication required",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="Please authenticate to access this resource.",
            troubleshooting_hints=["Check your credentials", "Ensure your session hasn't expired"]
        )
    
    @classmethod
    def invalid_credentials(cls, correlation_id: Optional[str] = None) -> "AuthenticationErrorResponse":
        """Create invalid credentials error response."""
        return cls(
            error_code="INVALID_CREDENTIALS",
            message="Invalid authentication credentials",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="The provided credentials are invalid. Please check and try again.",
            troubleshooting_hints=["Verify your username and password", "Check for typos"]
        )


class AuthorizationErrorResponse(BaseErrorResponse):
    """Error response model for authorization errors."""
    category: ErrorCategory = ErrorCategory.AUTHORIZATION
    required_permissions: Optional[List[str]] = Field(None, description="Required permissions")
    user_permissions: Optional[List[str]] = Field(None, description="User's current permissions")
    
    @classmethod
    def forbidden(cls, resource: str, correlation_id: Optional[str] = None) -> "AuthorizationErrorResponse":
        """Create forbidden error response."""
        return cls(
            error_code="FORBIDDEN",
            message=f"Access denied to {resource}",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="You don't have permission to access this resource.",
            troubleshooting_hints=["Contact your administrator for access", "Check if you have the required permissions"]
        )
    
    @classmethod
    def insufficient_permissions(cls, required: List[str], user: List[str], correlation_id: Optional[str] = None) -> "AuthorizationErrorResponse":
        """Create insufficient permissions error response."""
        return cls(
            error_code="INSUFFICIENT_PERMISSIONS",
            message=f"Insufficient permissions. Required: {', '.join(required)}",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message="You don't have the required permissions to perform this action.",
            troubleshooting_hints=["Contact your administrator to request additional permissions"],
            required_permissions=required,
            user_permissions=user
        )


class BusinessLogicErrorResponse(BaseErrorResponse):
    """Error response model for business logic errors."""
    category: ErrorCategory = ErrorCategory.BUSINESS_LOGIC
    business_rule: Optional[str] = Field(None, description="Business rule that was violated")
    entity_type: Optional[str] = Field(None, description="Entity type involved in the error")
    entity_id: Optional[str] = Field(None, description="Entity identifier")
    
    @classmethod
    def resource_not_found(cls, resource_type: str, resource_id: str, correlation_id: Optional[str] = None) -> "BusinessLogicErrorResponse":
        """Create resource not found error response."""
        return cls(
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource_type} not found: {resource_id}",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message=f"The requested {resource_type.lower()} could not be found.",
            troubleshooting_hints=["Verify the resource ID is correct", "Check if the resource was recently deleted"],
            entity_type=resource_type,
            entity_id=resource_id
        )
    
    @classmethod
    def invalid_state(cls, entity_type: str, entity_id: str, current_state: str, correlation_id: Optional[str] = None) -> "BusinessLogicErrorResponse":
        """Create invalid state error response."""
        return cls(
            error_code="INVALID_STATE",
            message=f"Invalid state for {entity_type} {entity_id}: {current_state}",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message=f"The {entity_type.lower()} is in an invalid state for this operation.",
            troubleshooting_hints=["Check the current state of the resource", "Verify the operation is valid for this state"],
            entity_type=entity_type,
            entity_id=entity_id
        )


class SystemErrorResponse(BaseErrorResponse):
    """Error response model for system errors."""
    category: ErrorCategory = ErrorCategory.SYSTEM
    component: Optional[str] = Field(None, description="System component that failed")
    stack_trace: Optional[str] = Field(None, description="Stack trace (development only)")
    
    @classmethod
    def internal_error(cls, component: str, correlation_id: Optional[str] = None) -> "SystemErrorResponse":
        """Create internal error response."""
        return cls(
            error_code="INTERNAL_SERVER_ERROR",
            message=f"Internal server error in {component}",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.HIGH,
            user_friendly_message="An internal error occurred. Please try again later.",
            troubleshooting_hints=["Please try again in a few moments", "If the problem persists, contact support"],
            component=component
        )
    
    @classmethod
    def configuration_error(cls, component: str, setting: str, correlation_id: Optional[str] = None) -> "SystemErrorResponse":
        """Create configuration error response."""
        return cls(
            error_code="CONFIGURATION_ERROR",
            message=f"Configuration error in {component}: {setting}",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.HIGH,
            user_friendly_message="The system is not properly configured.",
            troubleshooting_hints=["Check system configuration", "Verify all required settings are present"],
            component=component
        )


class ExternalServiceErrorResponse(BaseErrorResponse):
    """Error response model for external service errors."""
    category: ErrorCategory = ErrorCategory.EXTERNAL_SERVICE
    service_name: Optional[str] = Field(None, description="Name of the external service")
    service_error_code: Optional[str] = Field(None, description="Error code from the external service")
    service_error_message: Optional[str] = Field(None, description="Error message from the external service")
    
    @classmethod
    def service_unavailable(cls, service_name: str, correlation_id: Optional[str] = None) -> "ExternalServiceErrorResponse":
        """Create service unavailable error response."""
        return cls(
            error_code="SERVICE_UNAVAILABLE",
            message=f"External service {service_name} is unavailable",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.HIGH,
            user_friendly_message=f"The {service_name} service is currently unavailable.",
            troubleshooting_hints=["Please try again in a few moments", "Check if the service is under maintenance"],
            service_name=service_name
        )
    
    @classmethod
    def service_error(cls, service_name: str, service_code: str, service_message: str, correlation_id: Optional[str] = None) -> "ExternalServiceErrorResponse":
        """Create external service error response."""
        return cls(
            error_code="EXTERNAL_SERVICE_ERROR",
            message=f"Error from {service_name}: {service_code}",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.MEDIUM,
            user_friendly_message=f"There was an error communicating with {service_name}.",
            troubleshooting_hints=["Please try again later", "Contact support if the problem persists"],
            service_name=service_name,
            service_error_code=service_code,
            service_error_message=service_message
        )


class RateLimitErrorResponse(BaseErrorResponse):
    """Error response model for rate limit errors."""
    category: ErrorCategory = ErrorCategory.RATE_LIMIT
    limit: Optional[int] = Field(None, description="Rate limit value")
    window: Optional[str] = Field(None, description="Rate limit window")
    retry_after: Optional[int] = Field(None, description="Seconds until retry")
    
    @classmethod
    def rate_limit_exceeded(cls, limit: int, window: str, retry_after: int, correlation_id: Optional[str] = None) -> "RateLimitErrorResponse":
        """Create rate limit exceeded error response."""
        return cls(
            error_code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit exceeded: {limit} requests per {window}",
            correlation_id=correlation_id or str(uuid4()),
            severity=ErrorSeverity.LOW,
            user_friendly_message="Too many requests. Please slow down and try again.",
            troubleshooting_hints=["Reduce your request frequency", "Wait before making another request"],
            limit=limit,
            window=window,
            retry_after=retry_after
        )


# Type alias for all error response types
ErrorResponse = Union[
    BaseErrorResponse,
    ValidationErrorResponse,
    AuthenticationErrorResponse,
    AuthorizationErrorResponse,
    BusinessLogicErrorResponse,
    SystemErrorResponse,
    ExternalServiceErrorResponse,
    RateLimitErrorResponse
]