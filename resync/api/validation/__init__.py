"""Enhanced input validation using pydantic models with strict validation rules."""

from .common import (
    BaseValidatedModel,
    ValidationPatterns,
    StringConstraints,
    NumericConstraints,
    ValidationSeverity,
    ValidationErrorResponse,
    sanitize_input,
    validate_string_length,
    validate_numeric_range,
    validate_pattern,
    validate_enum_value
)

from .agents import (
    AgentConfig,
    AgentCreateRequest,
    AgentUpdateRequest,
    AgentQueryParams,
    AgentBulkActionRequest
)

from .auth import (
    LoginRequest,
    TokenRequest,
    PasswordChangeRequest,
    UserRegistrationRequest,
    APIKeyRequest,
    MFARequest,
    TokenRefreshRequest,
    LogoutRequest
)

from .chat import (
    ChatMessage,
    WebSocketMessage,
    ChatSession,
    ChatHistoryRequest,
    MessageReaction,
    ChatExportRequest
)

from .query_params import (
    PaginationParams,
    SearchParams,
    FilterParams,
    SortParams,
    DateRangeParams,
    AgentQueryParams,
    SystemQueryParams,
    AuditQueryParams,
    FileQueryParams,
    CombinedQueryParams,
    SortOrder,
    FilterOperator
)

from .files import (
    FileUploadRequest,
    FileChunkUploadRequest,
    FileUpdateRequest,
    FileProcessingRequest,
    RAGUploadRequest,
    FileInfo,
    FileType,
    ProcessingStatus
)

from .monitoring import (
    SystemMetricRequest,
    CustomMetricRequest,
    AlertRequest,
    AlertQueryParams,
    HealthCheckRequest,
    LogQueryParams,
    PerformanceTestRequest,
    MetricType,
    AlertSeverity,
    AlertStatus,
    HealthStatus
)

from .middleware import (
    ValidationMiddleware,
    ValidationConfig,
    create_validation_middleware,
    validate_json_body,
    validate_query_params
)

from .config import (
    ValidationMode,
    SanitizationLevel,
    ValidationConfigModel,
    AgentValidationConfig,
    ChatValidationConfig,
    SecurityValidationConfig,
    RateLimitConfig,
    ValidationSettings,
    get_validation_settings,
    set_validation_settings
)

__all__ = [
    # Common validation utilities
    "BaseValidatedModel",
    "ValidationPatterns",
    "StringConstraints",
    "NumericConstraints",
    "ValidationSeverity",
    "ValidationErrorResponse",
    "sanitize_input",
    "validate_string_length",
    "validate_numeric_range",
    "validate_pattern",
    "validate_enum_value",
    
    # Agent validation models
    "AgentConfig",
    "AgentCreateRequest",
    "AgentUpdateRequest",
    "AgentQueryParams",
    "AgentBulkActionRequest",
    
    # Authentication validation models
    "LoginRequest",
    "TokenRequest",
    "PasswordChangeRequest",
    "UserRegistrationRequest",
    "APIKeyRequest",
    "MFARequest",
    "TokenRefreshRequest",
    "LogoutRequest",
    
    # Chat validation models
    "ChatMessage",
    "WebSocketMessage",
    "ChatSession",
    "ChatHistoryRequest",
    "MessageReaction",
    "ChatExportRequest",
    
    # Query parameter validation models
    "PaginationParams",
    "SearchParams",
    "FilterParams",
    "SortParams",
    "DateRangeParams",
    "AgentQueryParams",
    "SystemQueryParams",
    "AuditQueryParams",
    "FileQueryParams",
    "CombinedQueryParams",
    "SortOrder",
    "FilterOperator",
    
    # File upload validation models
    "FileUploadRequest",
    "FileChunkUploadRequest",
    "FileUpdateRequest",
    "FileProcessingRequest",
    "RAGUploadRequest",
    "FileInfo",
    "FileType",
    "ProcessingStatus",
    
    # Monitoring validation models
    "SystemMetricRequest",
    "CustomMetricRequest",
    "AlertRequest",
    "AlertQueryParams",
    "HealthCheckRequest",
    "LogQueryParams",
    "PerformanceTestRequest",
    "MetricType",
    "AlertSeverity",
    "AlertStatus",
    "HealthStatus",
    
    # Middleware
    "ValidationMiddleware",
    "ValidationConfig",
    "create_validation_middleware",
    "validate_json_body",
    "validate_query_params",
    
    # Configuration
    "ValidationMode",
    "SanitizationLevel",
    "ValidationConfigModel",
    "AgentValidationConfig",
    "ChatValidationConfig",
    "SecurityValidationConfig",
    "RateLimitConfig",
    "ValidationSettings",
    "get_validation_settings",
    "set_validation_settings"
]

# Version information
__version__ = "1.0.0"
__author__ = "Resync Team"
__description__ = "Enhanced input validation using pydantic models with strict validation rules"