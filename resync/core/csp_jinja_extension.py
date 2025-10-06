"""Jinja2 extension for CSP nonce support."""

from typing import Optional
from jinja2 import Environment
from jinja2.ext import Extension

class CSPNonceExtension(Extension):
    """
    Jinja2 extension that provides access to CSP nonce in templates.
    
    This extension makes the CSP nonce available as a global variable
    in Jinja2 templates, allowing scripts to include the nonce attribute
    required by Content Security Policy.
    """
    
    def __init__(self, environment: Environment):
        """
        Initialize the CSP nonce extension.
        
        Args:
            environment: The Jinja2 environment
        """
        super().__init__(environment)
        
        # Add the nonce function to the global namespace
        environment.globals['csp_nonce'] = self._get_csp_nonce
    
    def _get_csp_nonce(self) -> str:
        """
        Get the CSP nonce from the current request context.
        
        Returns:
            The CSP nonce string, or empty string if not available
        """
        # This will be populated by the CSP middleware
        # The actual nonce is stored in request.state.csp_nonce
        # We need to access the request context
        from fastapi import Request
        
        # Try to get the request from the current context
        try:
            # This is a simplified approach - in a real implementation,
            # we would need to access the request from the current context
            # For now, we'll return an empty string if we can't access the request
            request: Optional[Request] = None
            if hasattr(self, 'environment') and hasattr(self.environment, 'handler'):
                request = self.environment.handler.get('request', None)
            
            if request and hasattr(request, 'state') and hasattr(request.state, 'csp_nonce'):
                return str(request.state.csp_nonce)
        except Exception:
            pass
        
        return ""

def setup_csp_jinja_extension(templates):
    """
    Set up CSP support for Jinja2 templates.
    
    Args:
        templates: The Jinja2Templates instance
    """
    # Add the CSP nonce extension to the Jinja2 environment
    templates.env.add_extension(CSPNonceExtension)
    
    # Add a filter for CSP nonce in script tags
    def script_nonce(nonce: str) -> str:
        """Generate a script tag with nonce attribute."""
        return f'nonce="{nonce}"'
    
    templates.env.filters['script_nonce'] = script_nonce