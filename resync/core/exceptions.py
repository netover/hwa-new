"""
Custom exceptions for the Resync application.

This module defines a hierarchy of custom exceptions for the Resync application,
allowing for more specific error handling and better error messages.
"""


# Base Exceptions
class ResyncError(Exception):
    """Base exception for all Resync errors."""


class ConfigError(ResyncError):
    """Base exception for configuration-related errors."""


class NetworkError(ResyncError):
    """Base exception for network-related errors."""


class DataError(ResyncError):
    """Base exception for data-related errors."""


class SecurityError(ResyncError):
    """Base exception for security-related errors."""


class ProcessingError(ResyncError):
    """Base exception for processing-related errors."""


# Configuration Exceptions
class SettingsError(ConfigError):
    """Raised when there's an issue with application settings."""


class MissingConfigError(ConfigError):
    """Raised when a required configuration is missing."""


class InvalidConfigError(ConfigError):
    """Raised when a configuration is invalid."""


# Network Exceptions
class ConnectionFailedError(NetworkError):
    """Raised when a connection attempt fails."""


class APIError(NetworkError):
    """Raised when an API request fails."""


class WebSocketError(NetworkError):
    """Raised when a WebSocket operation fails."""


class TimeoutError(NetworkError):
    """Raised when a network operation times out."""


# Data Exceptions
class ValidationError(DataError):
    """Raised when data validation fails."""


class DataParsingError(DataError):
    """Raised when data parsing fails."""


class DatabaseError(DataError):
    """Raised when a database operation fails."""


class CacheError(DataError):
    """Raised when a cache operation fails."""


# Security Exceptions
class AuthenticationError(SecurityError):
    """Raised when authentication fails."""


class AuthorizationError(SecurityError):
    """Raised when authorization fails."""


class TokenError(SecurityError):
    """Raised when there's an issue with a token."""


# Processing Exceptions
class AgentError(ProcessingError):
    """Raised when an agent operation fails."""


class AuditError(ProcessingError):
    """Raised when an audit operation fails."""


class LLMError(ProcessingError):
    """Raised when an LLM operation fails."""


class MemoryError(ProcessingError):
    """Raised when a memory operation fails."""


class FileProcessingError(ProcessingError):
    """Raised when file processing fails."""


class KnowledgeGraphError(ProcessingError):
    """Raised when a knowledge graph operation fails."""
