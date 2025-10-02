"""Simple test script to verify CSP functionality."""

import sys
import os
import secrets
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.testclient import TestClient
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

# Create a simple CSP middleware for testing
class SimpleCSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        nonce = secrets.token_hex(16)
        
        # Store nonce in request state for template access
        request.state.csp_nonce = nonce
        
        csp_policy = f"default-src 'self'; script-src 'self' 'nonce-{nonce}'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        response.headers["Content-Security-Policy"] = csp_policy
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

# Create test app
app = FastAPI()
app.add_middleware(SimpleCSPMiddleware)
print("Simple CSP middleware added for testing")

# Create test templates directory
templates_dir = Path("test_templates")
templates_dir.mkdir(exist_ok=True)

# Create a simple test template
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
async def test_page(request: Request):
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/api/test")
async def api_test():
    return {"message": "API test"}

# Test the application
def test_csp_functionality():
    """Test CSP functionality."""
    client = TestClient(app)
    
    print("\n=== Testing CSP Functionality ===")
    
    # Test HTML endpoint
    response = client.get("/test")
    print(f"HTML endpoint status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ HTML endpoint accessible")
        
        # Check CSP headers
        csp_header = response.headers.get("Content-Security-Policy")
        if csp_header:
            print(f"✓ CSP header present: {csp_header}")
            
            # Check CSP policy structure
            required_directives = [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                "font-src 'self'",
                "connect-src 'self'",
                "frame-ancestors 'none'"
            ]
            
            for directive in required_directives:
                if directive in csp_header:
                    print(f"✓ {directive} found in CSP policy")
                else:
                    print(f"✗ {directive} missing from CSP policy")
        else:
            print("✗ CSP header missing")
        
        # Check other security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block"
        }
        
        for header, expected_value in security_headers.items():
            actual_value = response.headers.get(header)
            if actual_value == expected_value:
                print(f"✓ {header} header correct")
            else:
                print(f"✗ {header} header missing or incorrect: {actual_value}")
        
        # Check for nonce in HTML
        html_content = response.text
        if 'nonce=' in html_content:
            print("✓ Nonce attribute found in HTML")
            # Extract nonce value
            import re
            nonce_matches = re.findall(r'nonce="([^"]+)"', html_content)
            if nonce_matches:
                print(f"✓ Nonce value: {nonce_matches[0]}")
                # Check if nonce is in CSP header
                if nonce_matches[0] in csp_header:
                    print("✓ Nonce correctly included in CSP header")
                else:
                    print("✗ Nonce missing from CSP header")
        else:
            print("✗ Nonce attribute missing in HTML")
    
    # Test API endpoint
    api_response = client.get("/api/test")
    print(f"\nAPI endpoint status: {api_response.status_code}")
    
    if api_response.status_code == 200:
        print("✓ API endpoint accessible")
        
        # Check that API responses also have CSP headers
        api_csp_header = api_response.headers.get("Content-Security-Policy")
        if api_csp_header:
            print("✓ CSP header present on API response")
        else:
            print("✗ CSP header missing on API response")
    
    # Test nonce uniqueness
    print("\n=== Testing Nonce Uniqueness ===")
    nonces = []
    for i in range(3):
        resp = client.get("/test")
        html_content = resp.text
        import re
        nonce_matches = re.findall(r'nonce="([^"]+)"', html_content)
        if nonce_matches:
            nonces.append(nonce_matches[0])
    
    if len(set(nonces)) == len(nonces) and len(nonces) > 0:
        print("✓ All nonces are unique across requests")
    else:
        print("✗ Nonces are not unique across requests")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_csp_functionality()