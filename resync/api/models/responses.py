"""Modelos de resposta de erro padronizados (RFC 7807 - Problem Details).

Este módulo implementa o padrão RFC 7807 para respostas de erro HTTP,
fornecendo uma estrutura consistente e legível por máquina para comunicar
problemas aos clientes da API.

Referência: https://tools.ietf.org/html/rfc7807
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from resync.core.context import get_correlation_id
from resync.core.exceptions import BaseAppException, ErrorCode, ErrorSeverity

# ============================================================================
# PROBLEM DETAILS MODEL (RFC 7807)
# ============================================================================


class ProblemDetail(BaseModel):
    """Modelo de resposta de erro seguindo RFC 7807.

    Attributes:
        type: URI que identifica o tipo de problema
        title: Resumo curto e legível do problema
        status: Código de status HTTP
        detail: Explicação detalhada do problema
        instance: URI que identifica a ocorrência específica
        correlation_id: ID de correlação para rastreamento
        timestamp: Timestamp do erro
        errors: Lista de erros de validação (opcional)
        extensions: Campos adicionais específicos do problema
    """

    type: str = Field(
        ...,
        description="URI que identifica o tipo de problema",
        example="https://api.example.com/errors/validation-error",
    )

    title: str = Field(
        ...,
        description="Resumo curto e legível do problema",
        example="Validation Error",
    )

    status: int = Field(
        ..., description="Código de status HTTP", ge=100, le=599, example=400
    )

    detail: str = Field(
        ...,
        description="Explicação detalhada do problema",
        example="The request body contains invalid data",
    )

    instance: Optional[str] = Field(
        None,
        description="URI que identifica a ocorrência específica",
        example="/api/v1/users/123",
    )

    correlation_id: Optional[str] = Field(
        None,
        description="ID de correlação para rastreamento",
        example="550e8400-e29b-41d4-a716-446655440000",
    )

    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z",
        description="Timestamp do erro em formato ISO 8601",
        example="2024-01-15T10:30:00Z",
    )

    error_code: Optional[str] = Field(
        None,
        description="Código de erro interno da aplicação",
        example="VALIDATION_ERROR",
    )

    severity: Optional[str] = Field(
        None, description="Nível de severidade do erro", example="warning"
    )

    errors: Optional[List[Dict[str, Any]]] = Field(
        None, description="Lista de erros de validação detalhados"
    )

    class Config:
        """Configuração do modelo."""

        json_schema_extra = {
            "example": {
                "type": "https://api.example.com/errors/validation-error",
                "title": "Validation Error",
                "status": 400,
                "detail": "The email field is required",
                "instance": "/api/v1/users",
                "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2024-01-15T10:30:00Z",
                "error_code": "VALIDATION_ERROR",
                "severity": "warning",
                "errors": [
                    {
                        "field": "email",
                        "message": "This field is required",
                        "code": "required",
                    }
                ],
            }
        }


# ============================================================================
# VALIDATION ERROR MODEL
# ============================================================================


class ValidationErrorDetail(BaseModel):
    """Detalhe de um erro de validação.

    Attributes:
        field: Nome do campo com erro
        message: Mensagem de erro
        code: Código do erro de validação
        value: Valor fornecido (opcional)
    """

    field: str = Field(..., description="Nome do campo com erro", example="email")

    message: str = Field(
        ..., description="Mensagem de erro", example="This field is required"
    )

    code: str = Field(
        ..., description="Código do erro de validação", example="required"
    )

    value: Optional[Any] = Field(None, description="Valor fornecido (se aplicável)")


class ValidationProblemDetail(ProblemDetail):
    """Modelo específico para erros de validação.

    Extends ProblemDetail com lista de erros de validação.
    """

    errors: List[ValidationErrorDetail] = Field(
        ..., description="Lista de erros de validação"
    )


# ============================================================================
# SUCCESS RESPONSE MODELS
# ============================================================================


class SuccessResponse(BaseModel):
    """Modelo de resposta de sucesso padronizado.

    Attributes:
        success: Indica sucesso da operação
        data: Dados da resposta
        message: Mensagem opcional
        metadata: Metadados adicionais
    """

    success: bool = Field(True, description="Indica sucesso da operação")

    data: Any = Field(..., description="Dados da resposta")

    message: Optional[str] = Field(None, description="Mensagem opcional")

    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Metadados adicionais (paginação, etc.)"
    )


class PaginatedResponse(BaseModel):
    """Modelo de resposta paginada.

    Attributes:
        items: Lista de itens
        total: Total de itens
        page: Página atual
        page_size: Tamanho da página
        total_pages: Total de páginas
    """

    items: List[Any] = Field(..., description="Lista de itens da página atual")

    total: int = Field(..., description="Total de itens", ge=0)

    page: int = Field(..., description="Página atual", ge=1)

    page_size: int = Field(..., description="Tamanho da página", ge=1)

    total_pages: int = Field(..., description="Total de páginas", ge=0)

    has_next: bool = Field(..., description="Indica se há próxima página")

    has_previous: bool = Field(..., description="Indica se há página anterior")


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================


def create_problem_detail(
    exception: BaseAppException,
    instance: Optional[str] = None,
    base_url: str = "https://api.resync.com/errors",
) -> ProblemDetail:
    """Cria ProblemDetail a partir de uma exceção.

    Args:
        exception: Exceção da aplicação
        instance: URI da instância (opcional)
        base_url: URL base para tipos de erro

    Returns:
        ProblemDetail configurado
    """
    # Construir type URI
    error_type = f"{base_url}/{exception.error_code.value.lower().replace('_', '-')}"

    # Obter correlation ID do contexto se não fornecido
    correlation_id = exception.correlation_id or get_correlation_id()

    return ProblemDetail(
        type=error_type,
        title=exception.error_code.value.replace("_", " ").title(),
        status=exception.status_code,
        detail=exception.message,
        instance=instance,
        correlation_id=correlation_id,
        error_code=exception.error_code.value,
        severity=exception.severity.value,
        errors=(
            _format_details_as_errors(exception.details) if exception.details else None
        ),
    )


def create_validation_problem_detail(
    errors: List[ValidationErrorDetail],
    detail: str = "Validation failed",
    instance: Optional[str] = None,
) -> ValidationProblemDetail:
    """Cria ValidationProblemDetail.

    Args:
        errors: Lista de erros de validação
        detail: Mensagem detalhada
        instance: URI da instância

    Returns:
        ValidationProblemDetail configurado
    """
    correlation_id = get_correlation_id()

    return ValidationProblemDetail(
        type="https://api.resync.com/errors/validation-error",
        title="Validation Error",
        status=400,
        detail=detail,
        instance=instance,
        correlation_id=correlation_id,
        error_code=ErrorCode.VALIDATION_ERROR.value,
        severity=ErrorSeverity.WARNING.value,
        errors=errors,
    )


def _format_details_as_errors(details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Formata dicionário de detalhes como lista de erros.

    Args:
        details: Dicionário de detalhes

    Returns:
        Lista de erros formatados
    """
    errors = []

    for key, value in details.items():
        if isinstance(value, dict):
            # Se for dicionário aninhado, processar recursivamente
            errors.extend(_format_details_as_errors(value))
        else:
            errors.append({"field": key, "value": value, "message": str(value)})

    return errors


def create_success_response(
    data: Any, message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
) -> SuccessResponse:
    """Cria resposta de sucesso padronizada.

    Args:
        data: Dados da resposta
        message: Mensagem opcional
        metadata: Metadados adicionais

    Returns:
        SuccessResponse configurado
    """
    return SuccessResponse(success=True, data=data, message=message, metadata=metadata)


def create_paginated_response(
    items: List[Any], total: int, page: int, page_size: int
) -> PaginatedResponse:
    """Cria resposta paginada.

    Args:
        items: Lista de itens
        total: Total de itens
        page: Página atual
        page_size: Tamanho da página

    Returns:
        PaginatedResponse configurado
    """
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1,
    )


# ============================================================================
# RESPONSE HELPERS
# ============================================================================


def error_response(
    exception: BaseAppException, instance: Optional[str] = None
) -> Dict[str, Any]:
    """Cria resposta de erro a partir de exceção.

    Args:
        exception: Exceção da aplicação
        instance: URI da instância

    Returns:
        Dicionário com resposta de erro
    """
    problem = create_problem_detail(exception, instance)
    return problem.model_dump(exclude_none=True)


def success_response(
    data: Any, message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Cria resposta de sucesso.

    Args:
        data: Dados da resposta
        message: Mensagem opcional
        metadata: Metadados adicionais

    Returns:
        Dicionário com resposta de sucesso
    """
    response = create_success_response(data, message, metadata)
    return response.model_dump(exclude_none=True)


def paginated_response(
    items: List[Any], total: int, page: int, page_size: int
) -> Dict[str, Any]:
    """Cria resposta paginada.

    Args:
        items: Lista de itens
        total: Total de itens
        page: Página atual
        page_size: Tamanho da página

    Returns:
        Dicionário com resposta paginada
    """
    response = create_paginated_response(items, total, page, page_size)
    return response.model_dump()


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


class PaginatedResponse(BaseModel):
    """Modelo de resposta paginada com suporte a HATEOAS.

    Attributes:
        items: Lista de itens
        total: Total de itens
        page: Página atual
        page_size: Tamanho da página
        total_pages: Total de páginas
        has_next: Indica se há próxima página
        has_previous: Indica se há página anterior
        links: Links de navegação (HATEOAS)
    """

    items: List[Any] = Field(..., description="Lista de itens da página atual")

    total: int = Field(..., description="Total de itens", ge=0)

    page: int = Field(..., description="Página atual", ge=1)

    page_size: int = Field(..., description="Tamanho da página", ge=1)

    total_pages: int = Field(..., description="Total de páginas", ge=0)

    has_next: bool = Field(..., description="Indica se há próxima página")

    has_previous: bool = Field(..., description="Indica se há página anterior")

    links: Optional[Dict[str, Any]] = Field(
        None, alias="_links", description="Links de navegação (HATEOAS)"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "items": [{"id": "1", "name": "Item 1"}],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10,
                "has_next": True,
                "has_previous": False,
                "_links": {
                    "self": {
                        "href": "/api/v1/resources?page=1&page_size=10",
                        "rel": "self",
                    },
                    "next": {
                        "href": "/api/v1/resources?page=2&page_size=10",
                        "rel": "next",
                    },
                    "first": {
                        "href": "/api/v1/resources?page=1&page_size=10",
                        "rel": "first",
                    },
                    "last": {
                        "href": "/api/v1/resources?page=10&page_size=10",
                        "rel": "last",
                    },
                },
            }
        }
