"""
Custom exceptions for the Resync application.

This module defines a hierarchy of custom exceptions for the Resync application,
allowing for more specific error handling and better error messages.
"""

# Base Exceptions
class ResyncError(Exception):
    """Base exception for all Resync errors."""
    pass


class ConfigError(ResyncError):
    """Base exception for configuration-related errors."""
    pass


class NetworkError(ResyncError):
    """Base exception for network-related errors."""
    pass


class DataError(ResyncError):
    """Base exception for data-related errors."""
    pass


class SecurityError(ResyncError):
    """Base exception for security-related errors."""
    pass


class ProcessingError(ResyncError):
    """Base exception for processing-related errors."""
    pass


# Configuration Exceptions
class SettingsError(ConfigError):
    """Raised when there's an issue with application settings."""
    pass


class MissingConfigError(ConfigError):
    """Raised when a required configuration is missing."""
    pass


class InvalidConfigError(ConfigError):
    """Raised when a configuration is invalid."""
    pass


# Network Exceptions
class ConnectionFailedError(NetworkError):
    """Raised when a connection attempt fails."""
    pass


class APIError(NetworkError):
    """Raised when an API request fails."""
    pass


class WebSocketError(NetworkError):
    """Raised when a WebSocket operation fails."""
    pass


class TimeoutError(NetworkError):
    """Raised when a network operation times out."""
    pass


# Data Exceptions
class ValidationError(DataError):
    """Raised when data validation fails."""
    pass


class DataParsingError(DataError):
    """Raised when data parsing fails."""
    pass


class DatabaseError(DataError):
    """Raised when a database operation fails."""
    pass


class CacheError(DataError):
    """Raised when a cache operation fails."""
    pass


# Security Exceptions
class AuthenticationError(SecurityError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(SecurityError):
    """Raised when authorization fails."""
    pass


class TokenError(SecurityError):
    """Raised when there's an issue with a token."""
    pass


# Processing Exceptions
class AgentError(ProcessingError):
    """Raised when an agent operation fails."""
    pass


class AuditError(ProcessingError):
    """Raised when an audit operation fails."""
    pass


class LLMError(ProcessingError):
    """Raised when an LLM operation fails."""
    pass


class MemoryError(ProcessingError):
    """Raised when a memory operation fails."""
    pass


class FileProcessingError(ProcessingError):
    """Raised when file processing fails."""
    pass


class KnowledgeGraphError(ProcessingError):
    """Raised when a knowledge graph operation fails."""
    pass
