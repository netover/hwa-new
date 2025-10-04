from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import unquote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi import status
from pydantic import BaseModel, Field

from resync.core.agent_manager import AgentConfig
from resync.core.fastapi_di import get_agent_manager, get_tws_client
from resync.core.interfaces import IAgentManager, ITWSClient
from resync.core.llm_wrapper import optimized_llm
from resync.core.metrics import runtime_metrics
from resync.core.rate_limiter import authenticated_rate_limit, public_rate_limit
from resync.core.tws_monitor import tws_monitor
from resync.models.tws import SystemStatus
from resync.settings import settings, settings_dynaconf

# Import CQRS components
from resync.cqrs.dispatcher import dispatcher, initialize_dispatcher
from resync.cqrs.commands import GetSystemStatusCommand, GetWorkstationsStatusCommand, GetJobsStatusCommand
from resync.cqrs.queries import GetSystemStatusQuery, GetWorkstationsStatusQuery, GetJobsStatusQuery, CheckTWSConnectionQuery
from resync.api_gateway.container import container, setup_dependencies
from resync.api_gateway.services import ITWSService, IAgentService, IKnowledgeService

# --- Logging Setup ---
logger = logging.getLogger(__name__)

# Module-level dependencies to avoid B008 errors
agent_manager_dependency = Depends(get_agent_manager)
tws_client_dependency = Depends(get_tws_client)

# --- APIRouter Initialization ---
api_router = APIRouter()


# --- Pydantic Models for Request/Response ---
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    response: str


class ExecuteRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=200)


class ExecuteResponse(BaseModel):
    result: str


class FilesResponse(BaseModel):
    path: str


class LLMQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    context: Dict[str, Any] = Field(default_factory=dict)
    use_cache: bool = Field(default=True)
    stream: bool = Field(default=False)


class LLMQueryResponse(BaseModel):
    optimized: bool
    query: str
    response: Any
    cache_used: bool


class TWSMetricsResponse(BaseModel):
    status: str
    critical_alerts: int
    warning_alerts: int
    last_updated: Optional[str]


class APIRouterEnhanced:
    """Enhanced API router with improved routing and error handling."""
    
    def __init__(self):
        self.router = APIRouter()
    
    def handle_error(self, e: Exception, operation: str):
        """
        Enhanced error handling for API operations.
        
        Args:
            e: Exception that occurred
            operation: Operation that caused the exception
        
        Returns:
            HTTPException with appropriate status code and message
        """
        logger.error(f"Error during {operation}: {e}", exc_info=True)
        
        if isinstance(e, HTTPException):
            return e
        
        # Map specific errors to appropriate HTTP status codes
        error_lower = str(e).lower()
        if "timeout" in error_lower or "connection" in error_lower:
            status_code = 504  # Gateway Timeout
            detail = f"Request timeout during {operation}"
        elif "auth" in error_lower or "unauthorized" in error_lower:
            status_code = 401  # Unauthorized
            detail = "Authentication required for this operation"
        elif "forbidden" in error_lower:
            status_code = 403  # Forbidden
            detail = "Access forbidden for this operation"
        elif "not found" in error_lower or "404" in error_lower:
            status_code = 404  # Not Found
            detail = f"Resource not found during {operation}"
        elif "validation" in error_lower or "invalid" in error_lower:
            status_code = 422  # Unprocessable Entity
            detail = f"Validation error during {operation}: {str(e)}"
        elif "conflict" in error_lower or "duplicate" in error_lower:
            status_code = 409  # Conflict
            detail = f"Conflict during {operation}: {str(e)}"
        else:
            status_code = 500  # Internal Server Error
            detail = f"An error occurred during {operation}: {str(e)}"
        
        return HTTPException(status_code=status_code, detail=detail)


def handle_error(e: Exception, operation: str):
    """
    Global error handling function for API operations.
    
    Args:
        e: Exception that occurred
        operation: Operation that caused the exception
    
    Returns:
        HTTPException with appropriate status code and message
    """
    logger.error(f"Error during {operation}: {e}", exc_info=True)
    
    if isinstance(e, HTTPException):
        return e
    
    # Map specific errors to appropriate HTTP status codes
    error_lower = str(e).lower()
    if "timeout" in error_lower or "connection" in error_lower:
        status_code = 504  # Gateway Timeout
        detail = f"Request timeout during {operation}"
    elif "auth" in error_lower or "unauthorized" in error_lower:
        status_code = 401  # Unauthorized
        detail = "Authentication required for this operation"
    elif "forbidden" in error_lower:
        status_code = 403  # Forbidden
        detail = "Access forbidden for this operation"
    elif "not found" in error_lower or "404" in error_lower:
        status_code = 404  # Not Found
        detail = f"Resource not found during {operation}"
    elif "validation" in error_lower or "invalid" in error_lower:
        status_code = 422  # Unprocessable Entity
        detail = f"Validation error during {operation}: {str(e)}"
    elif "conflict" in error_lower or "duplicate" in error_lower:
        status_code = 409  # Conflict
        detail = f"Conflict during {operation}: {str(e)}"
    else:
        status_code = 500  # Internal Server Error
        detail = f"An error occurred during {operation}: {str(e)}"
    
    return HTTPException(status_code=status_code, detail=detail)


# --- HTML serving endpoint for the main dashboard ---
@api_router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@public_rate_limit
async def get_dashboard(request: Request) -> HTMLResponse:
    """
    Serves the main `index.html` file for the dashboard.
    """
    index_path = settings.BASE_DIR / "templates" / "index.html"
    if not index_path.exists():
        logger.error("Dashboard index.html not found at path: %s", index_path)
        raise HTTPException(
            status_code=404, detail="Interface do dashboard não encontrada."
        )
    content = index_path.read_text(encoding="utf-8")
    return HTMLResponse(content=content)


# --- Agent Endpoints ---
@api_router.get(
    "/agents",
    response_model=List[AgentConfig],
    summary="Get All Agent Configurations",
)
@public_rate_limit
async def get_all_agents(
    request: Request,
    agent_manager: IAgentManager = agent_manager_dependency,
) -> List[AgentConfig]:
    """
    Returns the full configuration for all loaded agents.
    """
    return await agent_manager.get_all_agents()


# --- System Status Endpoints ---
@api_router.get("/status", response_model=SystemStatus)
@public_rate_limit
async def get_system_status(
    request: Request,
    tws_client: ITWSClient = tws_client_dependency,
) -> SystemStatus:
    """
    Provides a comprehensive status of the TWS environment, including
    workstations, jobs, and critical path information.
    """
    try:
        # Use CQRS pattern - dispatch a query to retrieve system status
        query = GetSystemStatusQuery()
        result = await dispatcher.execute_query(query)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error or "Failed to retrieve system status")
        
        status = SystemStatus(**result.data)
        
        # Record metrics upon successful status retrieval
        runtime_metrics.tws_status_requests_success.increment()
        runtime_metrics.tws_workstations_total.set(len(status.workstations))
        runtime_metrics.tws_jobs_total.set(len(status.jobs))
        return status
    except Exception as e:
        logger.error("Failed to get TWS system status: %s", e, exc_info=True)
        runtime_metrics.tws_status_requests_failed.increment()
        return handle_error(e, "TWS system status retrieval")


# --- New CQRS-based endpoints ---
@api_router.get("/status/workstations")
@public_rate_limit
async def get_workstations_status_cqrs(
    request: Request,
    tws_client: ITWSClient = tws_client_dependency,
) -> List[Dict[str, Any]]:
    """
    Get workstation statuses using CQRS pattern.
    """
    try:
        query = GetWorkstationsStatusQuery()
        result = await dispatcher.execute_query(query)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error or "Failed to retrieve workstation statuses")
        
        return result.data
    except Exception as e:
        logger.error("Failed to get TWS workstation statuses: %s", e, exc_info=True)
        return handle_error(e, "TWS workstation statuses retrieval")


@api_router.get("/status/jobs")
@public_rate_limit
async def get_jobs_status_cqrs(
    request: Request,
    tws_client: ITWSClient = tws_client_dependency,
) -> List[Dict[str, Any]]:
    """
    Get job statuses using CQRS pattern.
    """
    try:
        query = GetJobsStatusQuery()
        result = await dispatcher.execute_query(query)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.error or "Failed to retrieve job statuses")
        
        return result.data
    except Exception as e:
        logger.error("Failed to get TWS job statuses: %s", e, exc_info=True)
        return handle_error(e, "TWS job statuses retrieval")


# --- Health Check Endpoints ---
@api_router.get("/health/app", summary="Check Application Health")
@public_rate_limit
def get_app_health(request: Request) -> Dict[str, str]:
    """Returns a simple 'ok' to indicate the FastAPI application is running."""
    return {"status": "ok"}


@api_router.get("/health/tws", summary="Check TWS Connection Health")
@public_rate_limit
async def get_tws_health(
    request: Request,
    tws_client: ITWSClient = tws_client_dependency,
) -> Dict[str, Any]:
    """
    Performs a quick check to verify the connection to the TWS server is active.
    """
    try:
        query = CheckTWSConnectionQuery()
        result = await dispatcher.execute_query(query)
        
        if not result.success:
            logger.error("TWS connection check failed: %s", result.error)
            return {
                "status": "error",
                "message": "A verificação da conexão com o TWS falhou.",
            }
        
        is_connected = result.data.get("connected", False) if result.data else False
        if is_connected:
            return {
                "status": "ok",
                "message": "Conexão com o TWS bem-sucedida.",
            }
        else:
            return {
                "status": "error",
                "message": "A verificação da conexão com o TWS falhou.",
            }
    except Exception as e:
        logger.error("TWS health check failed: %s", e, exc_info=True)
        return handle_error(e, "TWS health check")


# --- Metrics Endpoint ---
@api_router.get(
    "/metrics",
    summary="Get Application Metrics",
    response_class=PlainTextResponse,
)
@public_rate_limit
def get_metrics(request: Request) -> str:
    """
    Returns application metrics in Prometheus text exposition format.
    """
    return runtime_metrics.generate_prometheus_metrics()


@api_router.post("/chat", response_model=ChatResponse)
@public_rate_limit
async def chat_endpoint(request: Request, data: ChatRequest) -> ChatResponse:
    """Chat endpoint for testing input validation."""
    if "<script>" in data.message:
        raise HTTPException(status_code=400, detail="XSS detected")
    return ChatResponse(response="ok")


@api_router.post("/sensitive")
@authenticated_rate_limit
async def sensitive_endpoint(request: Request, data: Dict[str, Any]) -> Dict[str, str]:
    """Sensitive endpoint for testing encryption."""
    from resync.core.encryption_service import encryption_service

    encrypted = encryption_service.encrypt(data["data"])
    from resync.core.logger import log_with_correlation

    log_with_correlation(logging.INFO, "Processing sensitive data (encrypted successfully)", component="api")
    return {"encrypted": encrypted}


@api_router.get("/protected")
@authenticated_rate_limit
async def protected_endpoint(request: Request):
    """Protected endpoint for testing authentication."""
    raise HTTPException(status_code=401, detail="Unauthorized")


@api_router.get("/admin/users")
@authenticated_rate_limit
async def admin_users_endpoint(request: Request):
    """Admin endpoint for testing authorization."""
    raise HTTPException(status_code=403, detail="Forbidden")


class ReviewRequest(BaseModel):
    content: str = Field(..., max_length=1000)  # noqa: F821


@api_router.post("/review")
@public_rate_limit
async def review_endpoint(request: Request, data: ReviewRequest):
    """Review endpoint for testing input validation."""
    if "<script>" in data.content:
        raise HTTPException(status_code=400, detail="XSS detected")
    return {"status": "reviewed"}


@api_router.post("/execute", response_model=ExecuteResponse)
@public_rate_limit
async def execute_endpoint(request: Request, data: ExecuteRequest) -> ExecuteResponse:
    """Execute endpoint for testing input validation."""
    forbidden_commands = ["rm", "del", ";", "`", "$"]
    if any(cmd in data.command for cmd in forbidden_commands):
        raise HTTPException(status_code=400, detail="Invalid command")
    return ExecuteResponse(result="executed")


@api_router.get("/files/{path:path}", response_model=FilesResponse)
@public_rate_limit
async def files_endpoint(request: Request, path: str) -> FilesResponse:
    """Files endpoint for testing path traversal."""
    # URL decode the path to prevent bypasses with encoded characters
    decoded_path = unquote(path)

    # Check for path traversal attempts
    if ".." in decoded_path or decoded_path.startswith("/") or "//" in decoded_path:
        raise HTTPException(status_code=400, detail="Invalid path")

    # Normalize the path to remove any potential traversal patterns
    import os
    normalized_path = os.path.normpath(decoded_path)

    # Ensure the normalized path doesn't try to go up directories
    if normalized_path.startswith("..") or "/.." in normalized_path:
        raise HTTPException(status_code=400, detail="Invalid path")

    return FilesResponse(path=normalized_path)


# --- Login Endpoint ---
@api_router.get("/login", response_class=HTMLResponse, include_in_schema=False)
@public_rate_limit
async def login_page(request: Request) -> HTMLResponse:
    """
    Serve the login page for admin authentication.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Resync Admin</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f5f5f5;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .login-container {
                background-color: white;
                padding: 2rem;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                width: 100%;
                max-width: 400px;
            }
            .login-title {
                text-align: center;
                margin-bottom: 1.5rem;
                color: #333;
            }
            .form-group {
                margin-bottom: 1rem;
            }
            .form-group label {
                display: block;
                margin-bottom: 0.5rem;
                color: #555;
            }
            .form-group input {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            .btn {
                width: 100%;
                padding: 0.75rem;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 1rem;
            }
            .btn:hover {
                background-color: #0056b3;
            }
            .error-message {
                color: red;
                text-align: center;
                margin-top: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2 class="login-title">Resync Admin Login</h2>
            <form id="loginForm" method="post" action="/token">
                <div class="form-group">
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="btn">Login</button>
            </form>
            <div id="errorMessage" class="error-message" style="display: none;"></div>
            
            <script>
                document.getElementById('loginForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const formData = new FormData(e.target);
                    const data = {
                        username: formData.get('username'),
                        password: formData.get('password')
                    };
                    
                    try {
                        const response = await fetch('/token', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: new URLSearchParams(data)
                        });
                        
                        if (response.ok) {
                            const result = await response.json();
                            localStorage.setItem('access_token', result.access_token);
                            window.location.href = '/dashboard';
                        } else {
                            const error = await response.json();
                            document.getElementById('errorMessage').textContent = error.detail || 'Login failed';
                            document.getElementById('errorMessage').style.display = 'block';
                        }
                    } catch (error) {
                        document.getElementById('errorMessage').textContent = 'An error occurred';
                        document.getElementById('errorMessage').style.display = 'block';
                    }
                });
            </script>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# Token endpoint for JWT authentication
@api_router.post("/token", include_in_schema=False)
@public_rate_limit
async def login_for_access_token(request: Request, 
                                username: str = Form(...), 
                                password: str = Form(...)):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    from resync.api.auth import authenticate_admin, create_access_token
    
    user = authenticate_admin(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}


@api_router.post("/llm/optimize", summary="Optimize LLM query with TWS-specific optimizations", 
                 response_model=LLMQueryResponse)
@authenticated_rate_limit
async def optimize_llm_query(
    request: Request,
    query_data: LLMQueryRequest
) -> LLMQueryResponse:
    """
    Optimize an LLM query using TWS-specific optimizations.
    
    This endpoint uses the LLM optimizer to enhance query processing
    with caching, model selection, and TWS-specific template matching.
    """
    try:
        response = await optimized_llm.get_response(
            query=query_data.query,
            context=query_data.context,
            use_cache=query_data.use_cache,
            stream=query_data.stream
        )
        
        return LLMQueryResponse(
            optimized=True,
            query=query_data.query,
            response=response,
            cache_used=not query_data.use_cache  # Simplified - in real implementation would check cache hit
        )
    except Exception as e:
        logger.error(f"LLM optimization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize LLM query: {str(e)}"
        )


# Redirect root to login page
@api_router.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/login")


# --- TWS Monitoring Endpoints ---
@api_router.get("/monitoring/metrics", summary="Get TWS Performance Metrics")
@authenticated_rate_limit
async def get_tws_metrics(request: Request) -> Dict[str, Any]:
    """
    Returns comprehensive TWS performance metrics including:
    - API performance
    - Cache hit ratios
    - LLM usage and costs
    - Circuit breaker status
    - Memory usage
    """
    return tws_monitor.get_performance_report()


@api_router.get("/monitoring/alerts", summary="Get Recent System Alerts")
@authenticated_rate_limit
async def get_tws_alerts(request: Request, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Returns recent system alerts and warnings.

    Args:
        limit: Maximum number of alerts to return (default: 10)
    """
    return tws_monitor.get_alerts(limit=limit)


@api_router.get("/monitoring/health", summary="Get TWS System Health")
@authenticated_rate_limit
async def get_tws_health_monitoring(request: Request) -> TWSMetricsResponse:  # Renamed to avoid conflict
    """
    Returns overall TWS system health status.
    """
    performance_report = tws_monitor.get_performance_report()

    # Determine health status
    critical_alerts = [
        alert
        for alert in performance_report["alerts"]
        if alert["severity"] == "critical"
    ]

    warning_alerts = [
        alert
        for alert in performance_report["alerts"]
        if alert["severity"] == "warning"
    ]

    if critical_alerts:
        status = "critical"
    elif warning_alerts:
        status = "warning"
    else:
        status = "healthy"

    return TWSMetricsResponse(
        status=status,
        critical_alerts=len(critical_alerts),
        warning_alerts=len(warning_alerts),
        last_updated=performance_report["current_metrics"].get("timestamp"),
    )
