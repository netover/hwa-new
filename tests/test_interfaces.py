"""Tests for resync.core.interfaces module."""

from resync.core.interfaces import (
    IAgentManager,
    IAuditQueue,
    IConnectionManager,
    IFileIngestor,
    IKnowledgeGraph,
    ITWSClient,
)


class TestInterfaceDefinitions:
    """Test suite for interface definitions."""

    def test_ifile_ingestor_is_protocol(self):
        """Test that IFileIngestor is a Protocol."""
        assert hasattr(IFileIngestor, "_is_protocol")
        assert IFileIngestor._is_protocol is True

    def test_iknowledge_graph_is_protocol(self):
        """Test that IKnowledgeGraph is a Protocol."""
        assert hasattr(IKnowledgeGraph, "_is_protocol")
        assert IKnowledgeGraph._is_protocol is True

    def test_iagent_manager_is_protocol(self):
        """Test that IAgentManager is a Protocol."""
        assert hasattr(IAgentManager, "_is_protocol")
        assert IAgentManager._is_protocol is True

    def test_iconnection_manager_is_protocol(self):
        """Test that IConnectionManager is a Protocol."""
        assert hasattr(IConnectionManager, "_is_protocol")
        assert IConnectionManager._is_protocol is True

    def test_iaudit_queue_is_protocol(self):
        """Test that IAuditQueue is a Protocol."""
        assert hasattr(IAuditQueue, "_is_protocol")
        assert IAuditQueue._is_protocol is True

    def test_itws_client_is_protocol(self):
        """Test that ITWSClient is a Protocol."""
        assert hasattr(ITWSClient, "_is_protocol")
        assert ITWSClient._is_protocol is True


class TestInterfaceMethods:
    """Test suite for interface method definitions."""

    def test_ifile_ingestor_has_required_methods(self):
        """Test that IFileIngestor defines required methods."""
        interface_methods = [
            name for name in dir(IFileIngestor) if not name.startswith("_")
        ]
        assert len(interface_methods) > 0

    def test_iknowledge_graph_has_required_methods(self):
        """Test that IKnowledgeGraph defines required methods."""
        interface_methods = [
            name for name in dir(IKnowledgeGraph) if not name.startswith("_")
        ]
        assert len(interface_methods) > 0

    def test_iagent_manager_has_required_methods(self):
        """Test that IAgentManager defines required methods."""
        interface_methods = [
            name for name in dir(IAgentManager) if not name.startswith("_")
        ]
        assert len(interface_methods) > 0

    def test_iconnection_manager_has_required_methods(self):
        """Test that IConnectionManager defines required methods."""
        interface_methods = [
            name for name in dir(IConnectionManager) if not name.startswith("_")
        ]
        assert len(interface_methods) > 0

    def test_iaudit_queue_has_required_methods(self):
        """Test that IAuditQueue defines required methods."""
        interface_methods = [
            name for name in dir(IAuditQueue) if not name.startswith("_")
        ]
        assert len(interface_methods) > 0

    def test_itws_client_has_required_methods(self):
        """Test that ITWSClient defines required methods."""
        interface_methods = [
            name for name in dir(ITWSClient) if not name.startswith("_")
        ]
        assert len(interface_methods) > 0


class TestInterfaceImplementation:
    """Test suite for interface implementation patterns."""

    def test_interfaces_exist_and_are_protocols(self):
        """Test that interfaces exist and are protocols."""
        interfaces = [
            IFileIngestor,
            IKnowledgeGraph,
            IAgentManager,
            IConnectionManager,
            IAuditQueue,
            ITWSClient,
        ]

        for interface in interfaces:
            assert hasattr(interface, "_is_protocol")
            assert interface._is_protocol is True
            assert interface.__doc__ is not None

    def test_interface_basic_functionality(self):
        """Test basic interface functionality."""
        # Test that interfaces have methods
        assert hasattr(IFileIngestor, "ingest_file")
        assert hasattr(IKnowledgeGraph, "add_conversation")
        assert hasattr(IAgentManager, "get_agent")
        assert hasattr(IConnectionManager, "broadcast")
        assert hasattr(IAuditQueue, "add_audit_record")
        assert hasattr(ITWSClient, "get_system_status")
