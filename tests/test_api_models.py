"""Tests for resync.api.models module."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from resync.api.models import (
    BaseModelWithTime,
    LoginRequest,
    Token,
    TokenData,
    RAGFileMetaData,
    RAGFileCreate,
    RAGFileDetail,
    AgentType,
    AgentConfig,
    SystemHealthStatus,
    SystemMetric,
    PaginationRequest,
    PaginationResponse,
)


class TestBaseModelWithTime:
    """Test BaseModelWithTime model."""

    def test_base_model_with_time_creation(self):
        """Test creating a BaseModelWithTime instance."""
        model = BaseModelWithTime()
        assert model.created_at is None
        assert model.updated_at is None

    def test_base_model_with_time_with_dates(self):
        """Test BaseModelWithTime with datetime values."""
        now = datetime.now()
        model = BaseModelWithTime(created_at=now, updated_at=now)
        assert model.created_at == now
        assert model.updated_at == now


class TestLoginRequest:
    """Test LoginRequest model."""

    def test_valid_login_request(self):
        """Test creating a valid login request."""
        login = LoginRequest(username="testuser", password="testpass")
        assert login.username == "testuser"
        assert login.password == "testpass"

    def test_login_request_missing_username(self):
        """Test login request with missing username."""
        with pytest.raises(ValidationError):
            LoginRequest(password="testpass")

    def test_login_request_missing_password(self):
        """Test login request with missing password."""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser")

    def test_login_request_empty_strings(self):
        """Test login request with empty strings."""
        login = LoginRequest(username="", password="")
        assert login.username == ""
        assert login.password == ""


class TestToken:
    """Test Token model."""

    def test_valid_token(self):
        """Test creating a valid token."""
        token = Token(access_token="abc123", token_type="bearer")
        assert token.access_token == "abc123"
        assert token.token_type == "bearer"

    def test_token_missing_fields(self):
        """Test token with missing fields."""
        with pytest.raises(ValidationError):
            Token(access_token="abc123")
        
        with pytest.raises(ValidationError):
            Token(token_type="bearer")


class TestTokenData:
    """Test TokenData model."""

    def test_token_data_with_username(self):
        """Test token data with username."""
        token_data = TokenData(username="testuser")
        assert token_data.username == "testuser"

    def test_token_data_without_username(self):
        """Test token data without username."""
        token_data = TokenData()
        assert token_data.username is None


class TestRAGFileMetaData:
    """Test RAGFileMetaData model."""

    def test_valid_rag_file_metadata(self):
        """Test creating valid RAG file metadata."""
        metadata = RAGFileMetaData(
            filename="test.pdf",
            content_type="application/pdf"
        )
        assert metadata.filename == "test.pdf"
        assert metadata.content_type == "application/pdf"
        assert metadata.uploaded_by is None
        assert metadata.description is None

    def test_rag_file_metadata_with_optional_fields(self):
        """Test RAG file metadata with optional fields."""
        metadata = RAGFileMetaData(
            filename="test.pdf",
            content_type="application/pdf",
            uploaded_by="user123",
            description="Test document"
        )
        assert metadata.uploaded_by == "user123"
        assert metadata.description == "Test document"


class TestRAGFileCreate:
    """Test RAGFileCreate model."""

    def test_valid_rag_file_create(self):
        """Test creating valid RAG file create model."""
        file_create = RAGFileCreate(
            filename="test.pdf",
            content_type="application/pdf"
        )
        assert file_create.filename == "test.pdf"
        assert file_create.content_type == "application/pdf"
        assert file_create.metadata is None

    def test_rag_file_create_with_metadata(self):
        """Test RAG file create with metadata."""
        metadata = RAGFileMetaData(
            filename="test.pdf",
            content_type="application/pdf",
            uploaded_by="user123"
        )
        file_create = RAGFileCreate(
            filename="test.pdf",
            content_type="application/pdf",
            metadata=metadata
        )
        assert file_create.metadata is not None
        assert file_create.metadata.uploaded_by == "user123"


class TestRAGFileDetail:
    """Test RAGFileDetail model."""

    def test_valid_rag_file_detail(self):
        """Test creating valid RAG file detail."""
        file_detail = RAGFileDetail(
            id="file123",
            filename="test.pdf",
            content_type="application/pdf",
            file_size=1024,
            ingestion_status="completed"
        )
        assert file_detail.id == "file123"
        assert file_detail.filename == "test.pdf"
        assert file_detail.content_type == "application/pdf"
        assert file_detail.file_size == 1024
        assert file_detail.ingestion_status == "completed"


class TestAgentType:
    """Test AgentType enum."""

    def test_agent_type_values(self):
        """Test AgentType enum values."""
        assert AgentType.LOCAL_SCRIPT == "local_script"
        assert AgentType.EXTERNAL_API == "external_api"
        assert AgentType.DATABASE_QUERY == "database_query"

    def test_agent_type_in_list(self):
        """Test that all enum values are accessible."""
        types = list(AgentType)
        assert len(types) == 3
        assert AgentType.LOCAL_SCRIPT in types
        assert AgentType.EXTERNAL_API in types
        assert AgentType.DATABASE_QUERY in types


class TestAgentConfig:
    """Test AgentConfig model."""

    def test_valid_agent_config(self):
        """Test creating valid agent config."""
        config = AgentConfig(
            agent_id="agent123",
            name="Test Agent",
            type=AgentType.LOCAL_SCRIPT
        )
        assert config.agent_id == "agent123"
        assert config.name == "Test Agent"
        assert config.type == AgentType.LOCAL_SCRIPT
        assert config.description is None
        assert config.configuration == {}

    def test_agent_config_with_optional_fields(self):
        """Test agent config with optional fields."""
        config = AgentConfig(
            agent_id="agent123",
            name="Test Agent",
            type=AgentType.EXTERNAL_API,
            description="Test description",
            configuration={"url": "http://test.com", "timeout": 30}
        )
        assert config.description == "Test description"
        assert config.configuration["url"] == "http://test.com"
        assert config.configuration["timeout"] == 30

    def test_agent_config_missing_required_fields(self):
        """Test agent config with missing required fields."""
        with pytest.raises(ValidationError):
            AgentConfig(name="Test Agent", type=AgentType.LOCAL_SCRIPT)
        
        with pytest.raises(ValidationError):
            AgentConfig(agent_id="agent123", type=AgentType.LOCAL_SCRIPT)
        
        with pytest.raises(ValidationError):
            AgentConfig(agent_id="agent123", name="Test Agent")


class TestSystemHealthStatus:
    """Test SystemHealthStatus enum."""

    def test_system_health_status_values(self):
        """Test SystemHealthStatus enum values."""
        assert SystemHealthStatus.OK == "ok"
        assert SystemHealthStatus.WARNING == "warning"
        assert SystemHealthStatus.CRITICAL == "critical"

    def test_system_health_status_in_list(self):
        """Test that all enum values are accessible."""
        statuses = list(SystemHealthStatus)
        assert len(statuses) == 3
        assert SystemHealthStatus.OK in statuses
        assert SystemHealthStatus.WARNING in statuses
        assert SystemHealthStatus.CRITICAL in statuses


class TestSystemMetric:
    """Test SystemMetric model."""

    def test_valid_system_metric(self):
        """Test creating valid system metric."""
        metric = SystemMetric(
            metric_name="cpu_usage",
            value=75.5,
            status=SystemHealthStatus.WARNING
        )
        assert metric.metric_name == "cpu_usage"
        assert metric.value == 75.5
        assert metric.status == SystemHealthStatus.WARNING

    def test_system_metric_with_timestamps(self):
        """Test system metric with timestamps."""
        now = datetime.now()
        metric = SystemMetric(
            metric_name="memory_usage",
            value=80.0,
            status=SystemHealthStatus.CRITICAL,
            created_at=now,
            updated_at=now
        )
        assert metric.created_at == now
        assert metric.updated_at == now


class TestPaginationRequest:
    """Test PaginationRequest model."""

    def test_pagination_request_defaults(self):
        """Test pagination request with default values."""
        pagination = PaginationRequest()
        assert pagination.page == 1
        assert pagination.page_size == 10

    def test_pagination_request_custom_values(self):
        """Test pagination request with custom values."""
        pagination = PaginationRequest(page=3, page_size=25)
        assert pagination.page == 3
        assert pagination.page_size == 25

    def test_pagination_request_validation(self):
        """Test pagination request validation."""
        # Should accept positive values
        pagination = PaginationRequest(page=1, page_size=1)
        assert pagination.page == 1
        assert pagination.page_size == 1


class TestPaginationResponse:
    """Test PaginationResponse model."""

    def test_valid_pagination_response(self):
        """Test creating valid pagination response."""
        response = PaginationResponse(
            total_items=100,
            total_pages=10,
            current_page=3,
            page_size=10
        )
        assert response.total_items == 100
        assert response.total_pages == 10
        assert response.current_page == 3
        assert response.page_size == 10

    def test_pagination_response_zero_items(self):
        """Test pagination response with zero items."""
        response = PaginationResponse(
            total_items=0,
            total_pages=0,
            current_page=1,
            page_size=10
        )
        assert response.total_items == 0
        assert response.total_pages == 0

    def test_pagination_response_single_page(self):
        """Test pagination response with single page."""
        response = PaginationResponse(
            total_items=5,
            total_pages=1,
            current_page=1,
            page_size=10
        )
        assert response.total_items == 5
        assert response.total_pages == 1
        assert response.current_page == 1