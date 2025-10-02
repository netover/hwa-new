"""Content Security Policy (CSP) middleware for FastAPI."""

import logging
import secrets
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

logger = logging.getLogger(__name__)


class CSPMiddleware(BaseHTTPMiddleware):
    """
    Middleware that implements Content Security Policy (CSP) with nonce generation.
    
    This middleware generates cryptographically secure nonces for each request
    and adds appropriate CSP headers to protect against XSS and other attacks.
    """
    
    def __init__(self, app, report_only: bool = False):
        """
        Initialize CSP middleware.
        
        Args:
            app: The FastAPI application
            report_only: If True, CSP violations are reported but not enforced
        """
        super().__init__(app)
        self.report_only = report_only
        # Import settings lazily to avoid circular imports
        from resync.settings import settings
        self.report_uri = getattr(settings, "CSP_REPORT_URI", None)
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Process each request and add CSP headers.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint
            
        Returns:
            Response with CSP headers
        """
        # Generate cryptographically secure nonce for this request
        nonce = self._generate_nonce()
        
        # Store nonce in request state for template access
        request.state.csp_nonce = nonce
        
        # Generate CSP policy with the nonce
        csp_policy = self._generate_csp_policy(nonce)
        
        # Process the request
        response = await call_next(request)
        
        # Add CSP headers to response
        self._add_csp_headers(response, csp_policy)
        
        # Log CSP violations if configured
        if request.url.path == "/csp-violation-report":
            await self._handle_csp_violation_report(request)
        
        return response
    
    def _generate_nonce(self) -> str:
        """
        Generate a cryptographically secure nonce.
        
        Returns:
            A base64-encoded nonce string
        """
        # Generate 16 bytes of cryptographically secure random data
        nonce_bytes = secrets.token_bytes(16)
        # Convert to base64 for use in CSP
        return nonce_bytes.hex()
    
    def _generate_csp_policy(self, nonce: str) -> str:
        """
        Generate CSP policy directives.
        
        Args:
            nonce: The generated nonce for this request
            
        Returns:
            CSP policy string
        """
        # Base CSP directives
        directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'", f"'nonce-{nonce}'"],
            "style-src": ["'self'", "'unsafe-inline'"],  # Allow inline styles
            "img-src": ["'self'", "data:", "https:"],  # Allow data URLs and HTTPS images
            "font-src": ["'self'"],
            "connect-src": ["'self'"],  # Allow API calls to same origin
            "frame-ancestors": ["'none'"],  # Prevent clickjacking
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
        }
        
        # Add report-uri if configured
        if self.report_uri:
            directives["report-uri"] = [self.report_uri]
            
        # Build policy string
        policy_parts = []
        for directive, sources in directives.items():
            policy_parts.append(f"{directive} {' '.join(sources)}")
            
        return "; ".join(policy_parts)
    
    def _add_csp_headers(self, response: Response, csp_policy: str) -> None:
        """
        Add CSP headers to the response.
        
        Args:
            response: The response object
            csp_policy: The CSP policy string
        """
        header_name = "Content-Security-Policy-Report-Only" if self.report_only else "Content-Security-Policy"
        response.headers[header_name] = csp_policy
        
        # Also add X-Content-Type-Options for additional security
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Add X-Frame-Options for clickjacking protection
        response.headers["X-Frame-Options"] = "DENY"
        
        # Add X-XSS-Protection for legacy browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
    
    async def _handle_csp_violation_report(self, request: Request) -> None:
        """
        Handle CSP violation reports.
        
        Args:
            request: The request containing CSP violation report
        """
        try:
            # Get the violation report from request body
            if request.method == "POST":
                body = await request.body()
                logger.warning(f"CSP violation reported: {body.decode('utf-8', errors='ignore')}")
        except Exception as e:
            logger.error(f"Error processing CSP violation report: {e}")


def create_csp_middleware(app) -> CSPMiddleware:
    """
    Factory function to create CSP middleware with configuration from settings.
    
    Args:
        app: The FastAPI application
        
    Returns:
        Configured CSPMiddleware instance
    """
    # Import settings lazily to avoid circular imports
    from resync.settings import settings
    
    # Check if CSP should be in report-only mode
    report_only = getattr(settings, "CSP_REPORT_ONLY", False)
    
    # Check if CSP is enabled
    csp_enabled = getattr(settings, "CSP_ENABLED", True)
    
    if not csp_enabled:
        logger.info("CSP middleware disabled via settings")
        # Return a no-op middleware
        return BaseHTTPMiddleware(app)
    
    logger.info(f"CSP middleware initialized (report_only={report_only})")
    return CSPMiddleware(app, report_only=report_only)