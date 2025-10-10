from __future__ import annotations

import re
import secrets
from pathlib import Path
from typing import Any, Generator
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from resync.core.header_parser import CSPParser

# Create a simple CSP middleware for testing
class SimpleCSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        nonce = secrets.token_hex(16)
        request.state.csp_nonce = nonce
        
        csp_policy = f"default-src 'self'; script-src 'self' 'nonce-{nonce}'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        response.headers["Content-Security-Policy"] = csp_policy
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app = FastAPI()
app.add_middleware(SimpleCSPMiddleware)

# Set up templates
templates_dir = Path("test_templates")
templates_dir.mkdir(exist_ok=True)

test_template = """<!DOCTYPE html>
<html>
<head>
    <title>CSP Test</title>
</head>
<body>
    <h1>CSP Test Page</h1>
    <script nonce="{{ request.state.csp_nonce if request and request.state.csp_nonce else '' }}">
        console.log('Test script with nonce');
    </script>
</body>
</html>"""

with open(templates_dir / "test.html", "w") as f:
    f.write(test_template)

templates = Jinja2Templates(directory=templates_dir)

@app.get("/test")
async def test_page(request: Request) -> Any:
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/api/test")
async def api_test() -> dict[str, str]:
    return {"message": "API test"}

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
        # Cleanup template directory after test
        if templates_dir.exists():
            import shutil
            shutil.rmtree(templates_dir)

def _check_security_headers(response_headers: Any) -> None:
    """Helper to check for standard security headers."""
    security_headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block"
    }
    for header, expected_value in security_headers.items():
        assert header in response_headers, f"{header} header is missing"
        assert response_headers[header] == expected_value, f"{header} header has incorrect value"

def _check_csp_policy(csp_header: str) -> None:
    """Helper to check the structure of the CSP policy."""
    assert csp_header is not None
    required_directives = [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: https:",
        "font-src 'self'",
        "connect-src 'self'",
        "frame-ancestors 'none'",
    ]
    for directive in required_directives:
        assert directive in csp_header

def test_html_endpoint_headers(client: TestClient) -> None:
    """Test that the HTML endpoint returns correct security headers."""
    response = client.get("/test")
    assert response.status_code == 200
    _check_security_headers(response.headers)
    _check_csp_policy(response.headers.get("Content-Security-Policy"))

def test_nonce_functionality(client: TestClient) -> None:
    """Test that the nonce is correctly generated and included."""
    response = client.get("/test")
    assert response.status_code == 200
    html_content = response.text
    csp_header = response.headers.get("Content-Security-Policy")
    
    # Use CSPParser to verify nonce exists in CSP
    csp_directives = CSPParser.parse(csp_header)
    assert 'script-src' in csp_directives
    assert any('nonce-' in value for value in csp_directives['script-src'])
    
    # Verify nonce exists in HTML
    nonce_matches = re.findall(r'nonce="([^"]+)"', html_content)
    assert nonce_matches
    nonce_in_html = nonce_matches[0]
    assert nonce_in_html
    assert any(nonce_in_html in value for value in csp_directives['script-src'])

def test_api_endpoint_headers(client: TestClient) -> None:
    """Test that API endpoints also receive security headers."""
    response = client.get("/api/test")
    assert response.status_code == 200
    assert "Content-Security-Policy" in response.headers
    _check_security_headers(response.headers)

def test_nonce_uniqueness(client: TestClient) -> None:
    """Test that nonces are unique across multiple requests."""
    responses = [client.get("/test") for _ in range(3)]
    nonces = []
    for response in responses:
        html_content = response.text
        csp_header = response.headers.get("Content-Security-Policy")
        csp_directives = CSPParser.parse(csp_header)
        nonce_in_html = re.findall(r'nonce="([^"]+)"', html_content)[0]
        assert nonce_in_html in csp_directives['script-src']
        nonces.append(nonce_in_html)
    assert len(nonces) == 3
    assert len(set(nonces)) == len(nonces)

def test_csp_directives(client: TestClient) -> None:
    """Test additional CSP directives (base-uri, form-action)"""
    response = client.get("/test")
    csp_header = response.headers.get("Content-Security-Policy")
    csp_directives = CSPParser.parse(csp_header)
    
    # Verify base-uri directive exists
    assert 'base-uri' in csp_directives
    assert "'self'" in csp_directives['base-uri']
    
    # Verify form-action directive exists
    assert 'form-action' in csp_directives
    assert "'self'" in csp_directives['form-action']

# Add parameterized test for CSP directives
@pytest.mark.parametrize("directive,expected_value", [
    ("default-src", "'self'"),
    ("script-src", "'self' 'nonce-{nonce}'"),
    ("style-src", "'self' 'unsafe-inline'"),
    ("img-src", "'self' data: https:"),
    ("font-src", "'self'"),
    ("connect-src", "'self'"),
    ("frame-ancestors", "'none'"),
    ("base-uri", "'self'"),
    ("form-action", "'self'")
])
def test_csp_directive_values(client, directive, expected_value):
    """Test that all CSP directives have correct values"""
    response = client.get("/test")
    assert response.status_code == 200
    csp_header = response.headers.get("Content-Security-Policy")
    csp_directives = CSPParser.parse(csp_header)
    
    assert directive in csp_directives
    assert expected_value in csp_directives[directive]

# Add tests for base-uri and form-action directives
def test_base_uri_directive(client):
    response = client.get("/test")
    csp_header = response.headers.get("Content-Security-Policy")
    csp_directives = CSPParser.parse(csp_header)
    assert 'base-uri' in csp_directives
    assert "'self'" in csp_directives['base-uri']

def test_form_action_directive(client):
    response = client.get("/test")
    csp_header = response.headers.get("Content-Security-Policy")
    csp_directives = CSPParser.parse(csp_header)
    assert 'form-action' in csp_directives
    assert "'self'" in csp_directives['form-action']