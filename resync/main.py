from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from resync.api.admin import admin_router
from resync.api.agents import agents_router
from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.cors_monitoring import cors_monitor_router
from resync.api.endpoints import api_router
from resync.api.health import config_router, health_router
from resync.api.rag_upload import router as rag_upload_router
from resync.api.operations import router as operations_router
from resync.api.rfc_examples import router as rfc_examples_router
from resync.settings import settings

# --- Structured Logging Initialization (CRITICAL: Must be first) ---
from resync.core.structured_logger import configure_structured_logging, get_logger

# Configure logging before any other imports that might use it
configure_structured_logging(
    log_level=getattr(settings, 'LOG_LEVEL', 'INFO'),
    json_logs=getattr(settings, 'ENVIRONMENT', 'development') == "production",
    development_mode=getattr(settings, 'ENVIRONMENT', 'development') == "development"
)

logger = get_logger(__name__)

# Import CQRS and API Gateway components
from resync.cqrs.dispatcher import initialize_dispatcher
from resync.api_gateway.container import setup_dependencies


# --- Rate Limiter Initialization ---
from resync.core.rate_limiter import (
    dashboard_rate_limit,
    init_rate_limiter,
)


# Update the lifespan function to initialize CQRS and dependency injection
from contextlib import asynccontextmanager
from resync.core.container import app_container
from resync.core.interfaces import ITWSClient, IAgentManager, IKnowledgeGraph
import asyncio


@asynccontextmanager
async def lifespan_with_cqrs_and_di(app: FastAPI):
    # Startup
    # Get the required services from the DI container
    tws_client = await app_container.get(ITWSClient)
    agent_manager = await app_container.get(IAgentManager)
    knowledge_graph = await app_container.get(IKnowledgeGraph)
    
    # Initialize TWS monitor with the TWS client
    from resync.core.tws_monitor import get_tws_monitor
    tws_monitor_instance = await get_tws_monitor(tws_client)
    
    # Setup dependency injection
    setup_dependencies(tws_client, agent_manager, knowledge_graph)
    
    # Initialize CQRS dispatcher
    initialize_dispatcher(tws_client, tws_monitor_instance)
    
    # Initialize Idempotency Manager
    from resync.api.dependencies import initialize_idempotency_manager
    from redis.exceptions import (
        ConnectionError,
        TimeoutError,
        AuthenticationError,
        BusyLoadingError,
        ResponseError
    )
    import sys

    max_retries = 3
    base_backoff = 0.1
    max_backoff = 10

    # Validate Redis environment variables before attempting connection
    redis_url = getattr(settings, 'REDIS_URL', None)
    if not redis_url:
        logger.critical("CRITICAL: REDIS_URL environment variable not set")
        sys.exit(1) # Fail fast

    # Track startup metrics
    startup_metrics = {
        "redis_connection_attempts": 0,
        "redis_connection_failures": 0,
        "redis_authentication_failures": 0,
        "startup_duration_seconds": 0
    }
    startup_start_time = asyncio.get_event_loop().time()

    for attempt in range(max_retries):
        startup_metrics["redis_connection_attempts"] += 1

        try:
            # Try to get Redis client from container
            from resync.core.async_cache import get_redis_client
            redis_client = await get_redis_client()

            # Test connection before initializing
            await redis_client.ping()

            await initialize_idempotency_manager(redis_client)
            logger.info("idempotency_manager_initialized", storage="redis")

            # Record successful startup metrics
            startup_metrics["startup_duration_seconds"] = asyncio.get_event_loop().time() - startup_start_time
            logger.info(f"Redis startup completed in {startup_metrics['startup_duration_seconds']:.2f}s")
            break

        except (ConnectionError, TimeoutError, BusyLoadingError) as e:
            startup_metrics["redis_connection_failures"] += 1

            if attempt >= max_retries - 1:
                logger.critical(
                    "redis_unavailable",
                    reason="Max retries reached",
                    retries=max_retries,
                    metrics=startup_metrics,
                    error=str(e)
                )
                sys.exit(1)

            backoff = min(max_backoff, base_backoff * (2 ** attempt))
            logger.warning(
                f"Redis connection failed (attempt {attempt + 1}/{max_retries}): {e}. "
                f"Retrying in {backoff:.2f}s"
            )
            await asyncio.sleep(backoff)

        except AuthenticationError as e:
            startup_metrics["redis_authentication_failures"] += 1
            logger.critical("redis_authentication_failed", error=str(e))
            sys.exit(1)

        except ResponseError as e:
            # Handle ACL/permission errors
            if "NOAUTH" in str(e) or "WRONGPASS" in str(e):
                startup_metrics["redis_authentication_failures"] += 1
                logger.critical("redis_access_denied", error=str(e))
                sys.exit(1)
            else:
                # Other ResponseError - re-raise to be caught by generic handler
                raise

        except Exception as e:
            # Unexpected error - log complete details and fail-fast
            logger.critical(
                "redis_initialization_failed",
                reason="Unexpected error",
                error=str(e),
                exc_info=True
            )
            sys.exit(1)
    
    # Initialize distributed tracing
    logger.info("distributed_tracing_initialized")
    # Initialize alerting system
    logger.info("alerting_system_initialized")
    # Initialize runbook registry
    logger.info("runbook_registry_initialized")
    # Initialize benchmarking system
    logger.info("benchmarking_system_initialized")
    
    yield  # Application runs here
    
    # Shutdown
    # Cleanup happens in the lifecycle manager
    from resync.core.tws_monitor import shutdown_tws_monitor
    await shutdown_tws_monitor()


def validate_critical_settings():
    """Valida configurações críticas no startup."""
    # Configurações básicas obrigatórias
    required_settings = [
        'PROJECT_NAME', 'PROJECT_VERSION', 'DESCRIPTION'
    ]

    missing = [setting for setting in required_settings
               if not getattr(settings, setting, None)]

    if missing:
        logger.critical(
            "missing_critical_settings", missing_settings=missing
        )
        raise ValueError(f"Missing critical settings: {', '.join(missing)}")

    # Validação específica para pools Redis
    redis_min = getattr(settings, "REDIS_POOL_MIN_SIZE", 5)
    redis_max = getattr(settings, "REDIS_POOL_MAX_SIZE", 20)

    if redis_min > redis_max:
        raise ValueError(
            f"Invalid Redis pool config: REDIS_POOL_MIN_SIZE ({redis_min}) > REDIS_POOL_MAX_SIZE ({redis_max})"
        )

    # Validação de configurações de segurança
    if getattr(settings, 'environment', 'development') == 'production':
        # Em produção, verificar se credenciais não são valores padrão
        admin_password = getattr(settings, 'ADMIN_PASSWORD', '')
        insecure_passwords = {'', 'change_me_immediately', 'PRODUCTION_PASSWORD_REQUIRED'}
        if admin_password in insecure_passwords:
            logger.critical(
                "insecure_admin_password",
                reason="Default or empty password used in production",
                environment="production"
            )
            raise ValueError("Production requires secure ADMIN_PASSWORD configuration")

# Validação no startup
validate_critical_settings()

# Use the updated lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan_with_cqrs_and_di,
)

# --- Configure CORS and Security Middleware ---
from resync.config.cors import configure_cors
from resync.config.csp import configure_csp
from resync.config.security import add_additional_security_headers

configure_cors(app, settings)
configure_csp(app, settings)
add_additional_security_headers(app)

# Initialize comprehensive rate limiting
init_rate_limiter(app)

# --- Register Exception Handlers ---
# Register the new standardized exception handlers
from resync.core.utils.error_utils import register_exception_handlers
register_exception_handlers(app)

from resync.core.fastapi_di import inject_container
# --- Dependency Injection Setup ---
# This should be done before including routers that might use DI
inject_container(app)

# Initialize audit queue if needed
# from resync.core.audit_queue import AsyncAuditQueue
# import asyncio


# --- Template Engine with Caching ---
from jinja2 import Environment, FileSystemLoader

# Create Jinja2 environment with caching and security
from jinja2 import select_autoescape

jinja2_env = Environment(
    loader=FileSystemLoader(str(settings.BASE_DIR / "templates")),
    auto_reload=getattr(settings, "DEBUG", False),  # Disable for production
    cache_size=getattr(settings, "JINJA2_TEMPLATE_CACHE_SIZE", 400 if not getattr(settings, "DEBUG", False) else 0),
    enable_async=True,
    autoescape=select_autoescape(enabled_extensions=('html', 'xml'), disabled_extensions=())
)

# Create templates and assign the environment
templates = Jinja2Templates(directory=str(settings.BASE_DIR / "templates"))
templates.env = jinja2_env

# --- Mount Routers and Static Files ---
app.include_router(api_router, prefix="/api")
app.include_router(admin_router, prefix="/api")  # Admin endpoints under /api/admin
app.include_router(rag_upload_router)
app.include_router(chat_router, prefix="/ws", tags=["WebSocket Chat"])
app.include_router(audit_router)
app.include_router(health_router)
app.include_router(config_router)
app.include_router(cors_monitor_router, prefix="/api/cors", tags=["CORS Monitoring"])
app.include_router(
    agents_router,
    prefix="/api/v1/agents",
    tags=["Agents"],
)
app.include_router(
    operations_router,
    tags=["Critical Operations"]
)
app.include_router(
    rfc_examples_router,
    tags=["RFC Examples"]
)

# Mount static files if directory exists
static_dir = settings.BASE_DIR / "static"
if static_dir.exists() and static_dir.is_dir():
    # from fastapi.staticfiles import StaticFiles
    from starlette.staticfiles import StaticFiles as StarletteStaticFiles
    
    import hashlib
    # import os

    class SecureCachedStaticFiles(StarletteStaticFiles):
        """Arquivos estáticos com cache seguro e ETags SHA-256."""

        async def get_response(self, path: str, full_path: str):
            response = await super().get_response(path, full_path)
            if response.status_code == 200:
                # Add cache headers for static files using configurable max-age
                cache_max_age = getattr(settings, "STATIC_CACHE_MAX_AGE", 3600)
                response.headers["Cache-Control"] = f"public, max-age={cache_max_age}"

                try:
                    import os
                    stat_result = os.stat(full_path)
                    # SHA-256 ao invés de MD5 para segurança
                    file_metadata = f"{stat_result.st_size}-{int(stat_result.st_mtime)}"
                    etag_value = f'"{hashlib.sha256(file_metadata.encode()).hexdigest()[:16]}"'
                    response.headers["ETag"] = etag_value
                except (OSError, ImportError) as e:
                    logger.warning("etag_generation_failed", path=path, error=str(e))
                    # Fallback seguro
                    response.headers["ETag"] = f'W/"{hash(full_path)}"' # Weak ETag
            return response
    
    app.mount(
        "/static",
        SecureCachedStaticFiles(directory=static_dir),
        name="static",
    )
    logger.info("static_files_mounted", directory=str(static_dir))
else:
    logger.warning("static_directory_not_found", path=str(static_dir))


# --- Frontend Page Endpoints ---
@app.get("/revisao", response_class=HTMLResponse, tags=["Frontend"])
@dashboard_rate_limit
async def get_review_page(request: Request) -> HTMLResponse:
    """
    Serves the main HTML page for the Human Review Dashboard.

    This dashboard allows human operators to review, approve, or reject
    agent interactions that were flagged by the IA Auditor for being
    potentially incorrect.
    """
    return templates.TemplateResponse("revisao.html", {"request": request})


def validate_csp_report(body: bytes) -> bool:
    """Validate CSP violation report format and content."""
    try:
        import json
        report_data = json.loads(body.decode('utf-8'))

        # Verificar estrutura básica do relatório
        if not isinstance(report_data, dict):
            return False

        # Verificar campos obrigatórios do CSP report
        required_fields = ['document-uri', 'violated-directive', 'original-policy']
        for field in required_fields:
            if field not in report_data and f'csp-report.{field}' not in report_data:
                # Verificar formato alternativo com csp-report prefixo
                if not any(key.startswith('csp-report.') for key in report_data.keys()):
                    return False

        # Verificar tamanho razoável (prevenir spam)
        if len(body) > 10000:  # 10KB limite
            return False

        return True
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
        return False

# --- CSP Violation Report Endpoint ---
@app.post("/csp-violation-report", include_in_schema=False)
async def csp_violation_report(request: Request):
    """Handle CSP violation reports with validation and rate limiting."""
    try:
        body = await request.body()

        # Validação do relatório CSP
        if not validate_csp_report(body):
            logger.warning("invalid_csp_report_received", client_host=request.client.host)
            raise HTTPException(status_code=400, detail="Invalid CSP report format")

        # Log limitado para prevenir vazamento de informações sensíveis
        report_preview = body.decode('utf-8', errors='ignore')[:500]
        logger.warning(
            "csp_violation_reported",
            client_host=request.client.host,
            report_preview=f"{report_preview}..."
        )

        return JSONResponse(content={"status": "received"}, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        # Log específico sem exposição de detalhes do erro
        logger.error("csp_report_processing_error", error_type=type(e).__name__)
        return JSONResponse(
            content={"error": "processing failed"},
            status_code=500
        )


@app.get("/", include_in_schema=False)
async def root():
    """Redirects the root URL to the login page."""
    return RedirectResponse(url="/login", status_code=302)


# Critical settings validation is handled by validate_critical_settings() above

# --- Application Entry Point (for direct execution) ---
if __name__ == "__main__":
    import uvicorn
    
    try:
        host = getattr(settings, 'server_host', '127.0.0.1')
        port = getattr(settings, 'server_port', 8000)
        logger.info("server_starting", host=host, port=port)
        # Use secure host binding from settings (defaults to 127.0.0.1 for security)
        uvicorn.run(
            "resync.main:app", # Use string to support reloading
            host=host,
            port=port,
            reload=getattr(settings, 'ENVIRONMENT', 'development') == 'development'
        )
    except Exception as e:
        logger.critical("server_startup_failed", error=str(e), exc_info=True)
        sys.exit(1)