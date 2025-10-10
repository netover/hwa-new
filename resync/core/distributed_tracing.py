"""
Distributed tracing implementation for Resync using OpenTelemetry
import asyncio
import os
from typing import Optional, Dict, Any
"""
import os
from typing import Optional, Dict, Any

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, Status, StatusCode
from fastapi import Request
from contextlib import contextmanager

from resync.settings import settings


class DistributedTracer:
    """
    Distributed tracing implementation using OpenTelemetry
    """
    
    def __init__(self):
        self.tracer = None
        self._setup_tracing()
    
    def _setup_tracing(self):
        """Setup OpenTelemetry tracing with Jaeger exporter"""
        # Configure tracer provider with resource attributes
        resource = Resource.create({
            "service.name": settings.PROJECT_NAME,
            "service.version": settings.PROJECT_VERSION,
            "environment": settings.environment
        })
        
        # Set up tracer provider
        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        # Configure Jaeger exporter
        if os.getenv("JAEGER_AGENT_HOST"):
            jaeger_exporter = JaegerExporter(
                agent_host_name=os.getenv("JAEGER_AGENT_HOST", "localhost"),
                agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
            )
            
            # Add span processor
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
        
        # Get tracer instance
        self.tracer = trace.get_tracer(__name__)
        
    def start_span(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> Span:
        """
        Start a new span with the given name and attributes
        """
        span = self.tracer.start_span(name, attributes=attributes or {})
        return span
    
    @contextmanager
    def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager to trace an operation
        """
        span = self.start_span(operation_name, attributes)
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            raise
        finally:
            span.end()
    
    def trace_fastapi_request(self, request: Request) -> Span:
        """
        Start a span for a FastAPI request
        """
        attributes = {
            "http.method": request.method,
            "http.url": str(request.url),
            "http.user_agent": request.headers.get("user-agent", ""),
            "http.client_ip": request.client.host if request.client else ""
        }
        
        span = self.start_span(f"HTTP {request.method} {request.url.path}", attributes)
        return span
    
    def add_span_attributes(self, span: Span, attributes: Dict[str, Any]):
        """
        Add attributes to an existing span
        """
        for key, value in attributes.items():
            span.set_attribute(key, value)
            
    def add_span_event(self, span: Span, name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Add an event to an existing span
        """
        span.add_event(name, attributes or {})


# Global tracer instance
tracer = DistributedTracer()


def get_tracer() -> DistributedTracer:
    """
    Get the global tracer instance
    """


def setup_tracing(service_name: str = None, service_version: str = None, environment: str = None) -> DistributedTracer:
    """
    Setup distributed tracing for the application.

    Args:
        service_name: Name of the service (optional)
        service_version: Version of the service (optional)
        environment: Environment name (optional)

    Returns:
        Configured tracer instance
    """
    global tracer

    # Update settings if provided
    if service_name:
        settings.PROJECT_NAME = service_name
    if service_version:
        settings.PROJECT_VERSION = service_version
    if environment:
        settings.environment = environment

    # Reinitialize tracer with new settings
    tracer = DistributedTracer()
    return tracer


def traced(operation_name: str = None, attributes: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace function execution.

    Args:
        operation_name: Name of the operation (defaults to function name)
        attributes: Additional attributes to add to the span
    """
    def decorator(func):
        span_name = operation_name or f"{func.__module__}.{func.__name__}"

        if asyncio.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                with tracer.trace_operation(span_name, attributes):
                    return await func(*args, **kwargs)
        else:
            def sync_wrapper(*args, **kwargs):
                with tracer.trace_operation(span_name, attributes):
                    return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator
    return tracer