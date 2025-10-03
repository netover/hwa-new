"""Módulo para exceções customizadas da aplicação Resync."""


class ResyncException(Exception):
    """Classe base para todas as exceções customizadas do Resync."""

    def __init__(self, message: str, original_exception: Exception | None = None):
        """
        Inicializa a exceção.

        Args:
            message: A mensagem de erro.
            original_exception: A exceção original que causou este erro, se houver.
        """
        super().__init__(message)
        self.original_exception = original_exception


class ConfigurationError(ResyncException):
    """Exceção para erros de configuração."""


class InvalidConfigError(ConfigurationError):
    """Exceção para erros de dados de configuração inválidos."""


class MissingConfigError(ConfigurationError):
    """Exceção para quando um arquivo de configuração não é encontrado."""


class AgentError(ResyncException):
    """Exceção para erros relacionados à criação ou gerenciamento de agentes."""


class TWSConnectionError(ResyncException):
    """Exceção para erros de conexão com a API do TWS."""


class AgentExecutionError(ResyncException):
    """Exceção para erros durante a execução de um agente de IA."""


class ToolExecutionError(ResyncException):
    """Exceção para erros durante a execução de uma ferramenta (tool)."""


class ToolConnectionError(ToolExecutionError):
    """Exceção para erros de conexão dentro de uma ferramenta."""


class ToolTimeoutError(ToolExecutionError):
    """Exceção para timeouts durante a execução de uma ferramenta."""


class ToolProcessingError(ToolExecutionError):
    """Exceção para erros de processamento de dados dentro de uma ferramenta."""


class KnowledgeGraphError(ResyncException):
    """Exceção para erros relacionados ao Knowledge Graph (ex: Mem0)."""


class AuditError(ResyncException):
    """Exceção para erros no sistema de auditoria (queue, lock, etc.)."""


class FileIngestionError(ResyncException):
    """Exceção para erros durante a ingestão de arquivos."""


class FileProcessingError(ResyncException):
    """Exceção para erros durante o processamento de arquivos."""


class LLMError(ResyncException):
    """Exceção para erros na comunicação com o Large Language Model."""


class ParsingError(ResyncException):
    """Exceção para erros de parsing de dados (JSON, etc.)."""


class DataParsingError(ParsingError):
    """Exceção para erros específicos de parsing de dados."""


class NetworkError(ResyncException):
    """Exceção para erros de rede genéricos."""


class WebSocketError(ResyncException):
    """Exceção para erros específicos de WebSocket."""


class DatabaseError(ResyncException):
    """Exceção para erros de interação com o banco de dados."""


class CacheError(ResyncException):
    """Exceção para erros relacionados ao sistema de cache."""


class NotificationError(ResyncException):
    """Exceção para erros durante o envio de notificações."""


class NotFoundError(ResyncException):
    """Exceção para quando um recurso não é encontrado."""


class NotFoundError(ResyncException):
    """Exceção para quando um recurso não é encontrado."""