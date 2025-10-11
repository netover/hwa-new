"""Modelos da API."""

from resync.api.models.responses import (
    ProblemDetail,
    ValidationErrorDetail,
    ValidationProblemDetail,
    SuccessResponse,
    PaginatedResponse,
    create_problem_detail,
    create_validation_problem_detail,
    create_success_response,
    create_paginated_response,
    error_response,
    success_response,
    paginated_response,
)

__all__ = [
    # Models
    "ProblemDetail",
    "ValidationErrorDetail",
    "ValidationProblemDetail",
    "SuccessResponse",
    "PaginatedResponse",
    # Factory Functions
    "create_problem_detail",
    "create_validation_problem_detail",
    "create_success_response",
    "create_paginated_response",
    # Response Helpers
    "error_response",
    "success_response",
    "paginated_response",
]
