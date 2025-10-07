"""Sistema de logging estruturado usando structlog.

Este módulo configura logging estruturado em formato JSON para facilitar
análise automatizada, agregação e monitoramento de logs.

Características:
- Logs em formato JSON
- Correlation ID automático
- Contexto enriquecido
- Níveis de log configuráveis por ambiente
- Integração com sistemas de agregação (ELK, Loki, etc.)
"""

import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime

import structlog
from structlog.types import EventDict, WrappedLogger

from resync.core.context import get_correlation_id, get_user_id, get_request_id


# ============================================================================
# PROCESSADORES CUSTOMIZADOS
# ============================================================================

def add_correlation_id(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Adiciona Correlation ID ao log.
    
    Args:
        logger: Logger
        method_name: Nome do método de log
        event_dict: Dicionário do evento
        
    Returns:
        Event dict com correlation_id
    """
    correlation_id = get_correlation_id()
    if correlation_id:
        event_dict['correlation_id'] = correlation_id
    return event_dict


def add_user_context(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Adiciona contexto do usuário ao log.
    
    Args:
        logger: Logger
        method_name: Nome do método de log
        event_dict: Dicionário do evento
        
    Returns:
        Event dict com user_id
    """
    user_id = get_user_id()
    if user_id:
        event_dict['user_id'] = user_id
    return event_dict


def add_request_context(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Adiciona contexto da requisição ao log.
    
    Args:
        logger: Logger
        method_name: Nome do método de log
        event_dict: Dicionário do evento
        
    Returns:
        Event dict com request_id
    """
    request_id = get_request_id()
    if request_id:
        event_dict['request_id'] = request_id
    return event_dict


def add_service_context(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Adiciona contexto do serviço ao log.
    
    Args:
        logger: Logger
        method_name: Nome do método de log
        event_dict: Dicionário do evento
        
    Returns:
        Event dict com service_name e environment
    """
    from resync.settings import settings
    
    event_dict['service_name'] = settings.PROJECT_NAME
    event_dict['environment'] = settings.environment
    event_dict['version'] = settings.PROJECT_VERSION
    
    return event_dict


def add_timestamp(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Adiciona timestamp ISO 8601 ao log.
    
    Args:
        logger: Logger
        method_name: Nome do método de log
        event_dict: Dicionário do evento
        
    Returns:
        Event dict com timestamp
    """
    event_dict['timestamp'] = datetime.utcnow().isoformat() + 'Z'
    return event_dict


def add_log_level(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Adiciona nível de log padronizado.
    
    Args:
        logger: Logger
        method_name: Nome do método de log
        event_dict: Dicionário do evento
        
    Returns:
        Event dict com level
    """
    if method_name == 'warn':
        method_name = 'warning'
    
    event_dict['level'] = method_name.upper()
    return event_dict


def censor_sensitive_data(
    logger: WrappedLogger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """Censura dados sensíveis nos logs.
    
    Args:
        logger: Logger
        method_name: Nome do método de log
        event_dict: Dicionário do evento
        
    Returns:
        Event dict com dados sensíveis censurados
    """
    sensitive_keys = {
        'password', 'token', 'secret', 'api_key', 'apikey',
        'authorization', 'auth', 'credential', 'private_key'
    }
    
    def censor_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Censura recursivamente um dicionário."""
        result = {}
        for key, value in d.items():
            key_lower = key.lower()
            
            # Verificar se a chave contém termo sensível
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                result[key] = '***REDACTED***'
            elif isinstance(value, dict):
                result[key] = censor_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    censor_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    return censor_dict(event_dict)


# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

def configure_structured_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    development_mode: bool = False
) -> None:
    """Configura logging estruturado para a aplicação.
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Se True, usa formato JSON; se False, formato legível
        development_mode: Se True, usa formato mais legível para desenvolvimento
    """
    # Configurar nível de log
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Processadores comuns
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        add_timestamp,
        add_log_level,
        add_correlation_id,
        add_user_context,
        add_request_context,
        add_service_context,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        censor_sensitive_data,
    ]
    
    # Processadores específicos por modo
    if development_mode or not json_logs:
        # Modo desenvolvimento: logs coloridos e legíveis
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Modo produção: logs em JSON
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    
    # Configurar structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Obtém um logger estruturado.
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
        
    Returns:
        Logger estruturado configurado
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


# ============================================================================
# HELPERS DE LOGGING
# ============================================================================

class LoggerAdapter:
    """Adapter para facilitar uso de logging estruturado.
    
    Fornece métodos convenientes para logging com contexto automático.
    """
    
    def __init__(self, logger: structlog.BoundLogger):
        """Inicializa o adapter.
        
        Args:
            logger: Logger estruturado
        """
        self.logger = logger
    
    def debug(self, event: str, **kwargs) -> None:
        """Log de debug."""
        self.logger.debug(event, **kwargs)
    
    def info(self, event: str, **kwargs) -> None:
        """Log de info."""
        self.logger.info(event, **kwargs)
    
    def warning(self, event: str, **kwargs) -> None:
        """Log de warning."""
        self.logger.warning(event, **kwargs)
    
    def error(
        self,
        event: str,
        exc_info: bool = False,
        **kwargs
    ) -> None:
        """Log de error.
        
        Args:
            event: Mensagem do evento
            exc_info: Se True, inclui informações da exceção
            **kwargs: Contexto adicional
        """
        if exc_info:
            import traceback
            kwargs['exc_info'] = traceback.format_exc()
        
        self.logger.error(event, **kwargs)
    
    def critical(
        self,
        event: str,
        exc_info: bool = False,
        **kwargs
    ) -> None:
        """Log de critical.
        
        Args:
            event: Mensagem do evento
            exc_info: Se True, inclui informações da exceção
            **kwargs: Contexto adicional
        """
        if exc_info:
            import traceback
            kwargs['exc_info'] = traceback.format_exc()
        
        self.logger.critical(event, **kwargs)
    
    def bind(self, **kwargs) -> 'LoggerAdapter':
        """Cria novo logger com contexto adicional.
        
        Args:
            **kwargs: Contexto a ser adicionado
            
        Returns:
            Novo LoggerAdapter com contexto
        """
        return LoggerAdapter(self.logger.bind(**kwargs))


def get_logger_adapter(name: Optional[str] = None) -> LoggerAdapter:
    """Obtém um logger adapter.
    
    Args:
        name: Nome do logger
        
    Returns:
        LoggerAdapter configurado
    """
    return LoggerAdapter(get_logger(name))


# ============================================================================
# LOGGING DE PERFORMANCE
# ============================================================================

class PerformanceLogger:
    """Logger especializado para métricas de performance."""
    
    def __init__(self, logger: structlog.BoundLogger):
        """Inicializa o performance logger.
        
        Args:
            logger: Logger estruturado
        """
        self.logger = logger
    
    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ) -> None:
        """Loga informações de uma requisição HTTP.
        
        Args:
            method: Método HTTP
            path: Caminho da requisição
            status_code: Código de status da resposta
            duration_ms: Duração em milissegundos
            **kwargs: Contexto adicional
        """
        self.logger.info(
            "http_request",
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=round(duration_ms, 2),
            **kwargs
        )
    
    def log_database_query(
        self,
        query_type: str,
        duration_ms: float,
        rows_affected: Optional[int] = None,
        **kwargs
    ) -> None:
        """Loga informações de uma query de banco de dados.
        
        Args:
            query_type: Tipo de query (SELECT, INSERT, etc.)
            duration_ms: Duração em milissegundos
            rows_affected: Número de linhas afetadas
            **kwargs: Contexto adicional
        """
        log_data = {
            "query_type": query_type,
            "duration_ms": round(duration_ms, 2),
        }
        
        if rows_affected is not None:
            log_data["rows_affected"] = rows_affected
        
        log_data.update(kwargs)
        
        self.logger.info("database_query", **log_data)
    
    def log_external_call(
        self,
        service_name: str,
        operation: str,
        duration_ms: float,
        success: bool,
        **kwargs
    ) -> None:
        """Loga chamada a serviço externo.
        
        Args:
            service_name: Nome do serviço
            operation: Operação realizada
            duration_ms: Duração em milissegundos
            success: Se a chamada foi bem-sucedida
            **kwargs: Contexto adicional
        """
        self.logger.info(
            "external_call",
            service_name=service_name,
            operation=operation,
            duration_ms=round(duration_ms, 2),
            success=success,
            **kwargs
        )


def get_performance_logger(name: Optional[str] = None) -> PerformanceLogger:
    """Obtém um performance logger.
    
    Args:
        name: Nome do logger
        
    Returns:
        PerformanceLogger configurado
    """
    return PerformanceLogger(get_logger(name))


__all__ = [
    # Configuração
    'configure_structured_logging',
    'get_logger',
    'get_logger_adapter',
    'get_performance_logger',
    # Classes
    'LoggerAdapter',
    'PerformanceLogger',
    # Processadores
    'add_correlation_id',
    'add_user_context',
    'add_request_context',
    'add_service_context',
    'add_timestamp',
    'add_log_level',
    'censor_sensitive_data',
]
