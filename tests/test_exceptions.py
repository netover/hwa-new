"""Tests for resync.core.exceptions module."""

import pytest

from resync.core.exceptions import (
    ResyncError,
    ConfigError,
    NetworkError,
    DataError,
    SecurityError,
    ProcessingError,
    SettingsError,
    MissingConfigError,
    InvalidConfigError,
    ConnectionFailedError,
    APIError,
    WebSocketError,
    TimeoutError,
    ValidationError,
    DataParsingError,
    DatabaseError,
    CacheError,
    AuthenticationError,
    AuthorizationError,
    TokenError,
    AgentError,
    AuditError,
    LLMError,
    MemoryError,
    FileProcessingError,
    KnowledgeGraphError,
)


class TestBaseExceptions:
    """Test suite for base exception classes."""

    def test_resync_error_basic(self):
        """Test ResyncError basic functionality."""
        error = ResyncError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_resync_error_empty_message(self):
        """Test ResyncError with empty message."""
        error = ResyncError("")
        assert str(error) == ""

    def test_resync_error_no_message(self):
        """Test ResyncError with no message."""
        error = ResyncError()
        assert str(error) == ""


class TestConfigExceptions:
    """Test suite for configuration exception classes."""

    def test_config_error_inheritance(self):
        """Test ConfigError inheritance."""
        error = ConfigError("Config error")
        assert isinstance(error, ResyncError)
        assert isinstance(error, Exception)

    def test_settings_error(self):
        """Test SettingsError functionality."""
        error = SettingsError("Settings error")
        assert str(error) == "Settings error"
        assert isinstance(error, ConfigError)

    def test_missing_config_error(self):
        """Test MissingConfigError functionality."""
        error = MissingConfigError("Missing config")
        assert str(error) == "Missing config"
        assert isinstance(error, ConfigError)

    def test_invalid_config_error(self):
        """Test InvalidConfigError functionality."""
        error = InvalidConfigError("Invalid config")
        assert str(error) == "Invalid config"
        assert isinstance(error, ConfigError)


class TestNetworkExceptions:
    """Test suite for network exception classes."""

    def test_network_error_inheritance(self):
        """Test NetworkError inheritance."""
        error = NetworkError("Network error")
        assert isinstance(error, ResyncError)
        assert isinstance(error, Exception)

    def test_connection_failed_error(self):
        """Test ConnectionFailedError functionality."""
        error = ConnectionFailedError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, NetworkError)

    def test_api_error(self):
        """Test APIError functionality."""
        error = APIError("API error")
        assert str(error) == "API error"
        assert isinstance(error, NetworkError)

    def test_websocket_error(self):
        """Test WebSocketError functionality."""
        error = WebSocketError("WebSocket error")
        assert str(error) == "WebSocket error"
        assert isinstance(error, NetworkError)

    def test_timeout_error(self):
        """Test TimeoutError functionality."""
        error = TimeoutError("Timeout error")
        assert str(error) == "Timeout error"
        assert isinstance(error, NetworkError)


class TestDataExceptions:
    """Test suite for data exception classes."""

    def test_data_error_inheritance(self):
        """Test DataError inheritance."""
        error = DataError("Data error")
        assert isinstance(error, ResyncError)
        assert isinstance(error, Exception)

    def test_validation_error(self):
        """Test ValidationError functionality."""
        error = ValidationError("Validation error")
        assert str(error) == "Validation error"
        assert isinstance(error, DataError)

    def test_data_parsing_error(self):
        """Test DataParsingError functionality."""
        error = DataParsingError("Parsing error")
        assert str(error) == "Parsing error"
        assert isinstance(error, DataError)

    def test_database_error(self):
        """Test DatabaseError functionality."""
        error = DatabaseError("Database error")
        assert str(error) == "Database error"
        assert isinstance(error, DataError)

    def test_cache_error(self):
        """Test CacheError functionality."""
        error = CacheError("Cache error")
        assert str(error) == "Cache error"
        assert isinstance(error, DataError)


class TestSecurityExceptions:
    """Test suite for security exception classes."""

    def test_security_error_inheritance(self):
        """Test SecurityError inheritance."""
        error = SecurityError("Security error")
        assert isinstance(error, ResyncError)
        assert isinstance(error, Exception)

    def test_authentication_error(self):
        """Test AuthenticationError functionality."""
        error = AuthenticationError("Auth error")
        assert str(error) == "Auth error"
        assert isinstance(error, SecurityError)

    def test_authorization_error(self):
        """Test AuthorizationError functionality."""
        error = AuthorizationError("Authz error")
        assert str(error) == "Authz error"
        assert isinstance(error, SecurityError)

    def test_token_error(self):
        """Test TokenError functionality."""
        error = TokenError("Token error")
        assert str(error) == "Token error"
        assert isinstance(error, SecurityError)


class TestProcessingExceptions:
    """Test suite for processing exception classes."""

    def test_processing_error_inheritance(self):
        """Test ProcessingError inheritance."""
        error = ProcessingError("Processing error")
        assert isinstance(error, ResyncError)
        assert isinstance(error, Exception)

    def test_agent_error(self):
        """Test AgentError functionality."""
        error = AgentError("Agent error")
        assert str(error) == "Agent error"
        assert isinstance(error, ProcessingError)

    def test_audit_error(self):
        """Test AuditError functionality."""
        error = AuditError("Audit error")
        assert str(error) == "Audit error"
        assert isinstance(error, ProcessingError)

    def test_llm_error(self):
        """Test LLMError functionality."""
        error = LLMError("LLM error")
        assert str(error) == "LLM error"
        assert isinstance(error, ProcessingError)

    def test_memory_error(self):
        """Test MemoryError functionality."""
        error = MemoryError("Memory error")
        assert str(error) == "Memory error"
        assert isinstance(error, ProcessingError)

    def test_file_processing_error(self):
        """Test FileProcessingError functionality."""
        error = FileProcessingError("File processing error")
        assert str(error) == "File processing error"
        assert isinstance(error, ProcessingError)

    def test_knowledge_graph_error(self):
        """Test KnowledgeGraphError functionality."""
        error = KnowledgeGraphError("Knowledge graph error")
        assert str(error) == "Knowledge graph error"
        assert isinstance(error, ProcessingError)


class TestExceptionHierarchy:
    """Test suite for exception hierarchy."""

    def test_exception_inheritance_chain(self):
        """Test that all exceptions follow the correct inheritance chain."""
        # Test base exception
        assert issubclass(ResyncError, Exception)

        # Test category exceptions
        assert issubclass(ConfigError, ResyncError)
        assert issubclass(NetworkError, ResyncError)
        assert issubclass(DataError, ResyncError)
        assert issubclass(SecurityError, ResyncError)
        assert issubclass(ProcessingError, ResyncError)

        # Test specific exceptions
        assert issubclass(SettingsError, ConfigError)
        assert issubclass(MissingConfigError, ConfigError)
        assert issubclass(InvalidConfigError, ConfigError)

        assert issubclass(ConnectionFailedError, NetworkError)
        assert issubclass(APIError, NetworkError)
        assert issubclass(WebSocketError, NetworkError)
        assert issubclass(TimeoutError, NetworkError)

        assert issubclass(ValidationError, DataError)
        assert issubclass(DataParsingError, DataError)
        assert issubclass(DatabaseError, DataError)
        assert issubclass(CacheError, DataError)

        assert issubclass(AuthenticationError, SecurityError)
        assert issubclass(AuthorizationError, SecurityError)
        assert issubclass(TokenError, SecurityError)

        assert issubclass(AgentError, ProcessingError)
        assert issubclass(AuditError, ProcessingError)
        assert issubclass(LLMError, ProcessingError)
        assert issubclass(MemoryError, ProcessingError)
        assert issubclass(FileProcessingError, ProcessingError)
        assert issubclass(KnowledgeGraphError, ProcessingError)

    def test_all_exceptions_are_resync_errors(self):
        """Test that all specific exceptions are ResyncError instances."""
        exceptions_to_test = [
            ConfigError("test"),
            NetworkError("test"),
            DataError("test"),
            SecurityError("test"),
            ProcessingError("test"),
            SettingsError("test"),
            MissingConfigError("test"),
            InvalidConfigError("test"),
            ConnectionFailedError("test"),
            APIError("test"),
            WebSocketError("test"),
            TimeoutError("test"),
            ValidationError("test"),
            DataParsingError("test"),
            DatabaseError("test"),
            CacheError("test"),
            AuthenticationError("test"),
            AuthorizationError("test"),
            TokenError("test"),
            AgentError("test"),
            AuditError("test"),
            LLMError("test"),
            MemoryError("test"),
            FileProcessingError("test"),
            KnowledgeGraphError("test"),
        ]

        for exception in exceptions_to_test:
            assert isinstance(exception, ResyncError)
            assert isinstance(exception, Exception)


class TestExceptionMessages:
    """Test suite for exception messages and formatting."""

    def test_exception_message_preservation(self):
        """Test that exception messages are properly preserved."""
        test_cases = [
            ("Simple message", "Simple message"),
            ("Message with spaces", "Message with spaces"),
            ("Message with special chars: @#$%^&*()", "Message with special chars: @#$%^&*()"),
            ("", ""),
            ("Message\nwith\nnewlines", "Message\nwith\nnewlines"),
        ]

        for message, expected in test_cases:
            error = ResyncError(message)
            assert str(error) == expected

    def test_exception_with_none_message(self):
        """Test exception with None message."""
        error = ResyncError(None)
        assert str(error) == "None"

    def test_exception_with_numeric_message(self):
        """Test exception with numeric message."""
        error = ResyncError(42)
        assert str(error) == "42"

    def test_exception_with_complex_message(self):
        """Test exception with complex message structure."""
        error = ResyncError({"key": "value", "number": 123})
        assert str(error) == "{'key': 'value', 'number': 123}"


class TestExceptionChaining:
    """Test suite for exception chaining."""

    def test_exception_chaining_with_cause(self):
        """Test exception chaining with __cause__."""
        original_error = ValueError("Original error")
        chained_error = ResyncError("Chained error")

        # Test that we can chain exceptions
        try:
            raise original_error
        except ValueError as e:
            try:
                raise chained_error from e
            except ResyncError as chained:
                assert chained.__cause__ is original_error
                assert isinstance(chained, ResyncError)

    def test_exception_chaining_with_context(self):
        """Test exception chaining with __context__."""
        original_error = ValueError("Original error")
        context_error = ResyncError("Context error")

        # Test that we can chain exceptions with context
        try:
            raise original_error
        except ValueError as e:
            try:
                raise context_error
            except ResyncError as chained:
                assert chained.__context__ is original_error
                assert isinstance(chained, ResyncError)

    def test_nested_exception_chaining(self):
        """Test nested exception chaining."""
        level1 = ValueError("Level 1")
        level2 = RuntimeError("Level 2")
        level3 = ResyncError("Level 3")

        try:
            raise level1
        except ValueError as e:
            try:
                raise level2 from e
            except RuntimeError as e2:
                try:
                    raise level3 from e2
                except ResyncError as e3:
                    assert e3.__cause__ is level2
                    assert level2.__cause__ is level1
                    assert isinstance(e3, ResyncError)


class TestExceptionEdgeCases:
    """Test suite for exception edge cases."""

    def test_exception_with_very_long_message(self):
        """Test exception with very long message."""
        long_message = "A" * 10000
        error = ResyncError(long_message)
        assert str(error) == long_message
        assert len(str(error)) == 10000

    def test_exception_with_unicode_message(self):
        """Test exception with Unicode characters."""
        unicode_message = "Test with émojis: 🚀 and ñ characters"
        error = ResyncError(unicode_message)
        assert str(error) == unicode_message

    def test_exception_with_binary_data(self):
        """Test exception with binary data as message."""
        binary_data = b"Binary data\x00\x01\x02"
        error = ResyncError(binary_data)
        assert str(error) == str(binary_data)

    def test_exception_inheritance_depth(self):
        """Test that inheritance depth is correct."""
        # Test that specific exceptions have the right inheritance depth
        error = FileProcessingError("test")

        # Should be instance of all parent classes
        assert isinstance(error, ProcessingError)
        assert isinstance(error, ResyncError)
        assert isinstance(error, Exception)

        # Should not be instance of sibling classes
        assert not isinstance(error, NetworkError)
        assert not isinstance(error, DataError)
        assert not isinstance(error, SecurityError)
        assert not isinstance(error, ConfigError)

    def test_multiple_instantiation(self):
        """Test that exceptions can be instantiated multiple times."""
        for i in range(100):
            error = ResyncError(f"Error {i}")
            assert str(error) == f"Error {i}"

    def test_exception_as_context_manager(self):
        """Test that exceptions work as context managers."""
        try:
            with pytest.raises(ResyncError):
                raise ResyncError("Context manager test")
        except ResyncError as e:
            assert str(e) == "Context manager test"



