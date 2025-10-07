"""Arquivo principal da aplicação Resync com melhorias de erro e qualidade.

Este arquivo integra todas as melhorias implementadas:
- Hierarquia de exceções customizadas
- Sistema de Correlation IDs
- Logging estruturado
- Padrões de resiliência
- Sistema de Idempotency Keys
- Respostas de erro padronizadas (RFC 7807)
- Exception handlers globais
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader

# Settings
from resync.settings import settings

# Logging estruturado
from resync.core.structured_logger import configure_structured_logging

# Middleware
from resync.api.middleware import CorrelationIdMiddleware

# Exception handlers
from resync.api.exception_handlers import register_exception_handlers

# Routers
from resync.api.admin import admin_router
from resync.api.agents import agents_router
from resync.api.audit import router as audit_router
from resync.api.chat import chat_router
from resync.api.cors_monitoring import cors_monitor_router
from resync.api.endpoints import api_router
from resync.api.health import config_router, health_router
from resync.api.rag_upload import router as rag_upload_router
from resync.api.performance import performance_router

# Core components
from resync.core.fastapi_di import inject_container
from resync.core.container import app_container
from resync.core.interfaces import ITWSClient, IAgentManager, IKnowledgeGraph

# CQRS and API Gateway
from resync.cqrs.dispatcher import initialize_dispatcher
from resync.api_gateway.container import setup_dependencies

# Rate limiter
from resync.core.rate_limiter import (
    dashboard_rate_limit,
    init_rate_limiter,
)

# CORS and Security
from resync.config.cors import configure_cors
from resync.config.csp import configure_csp
from resync.config.security import add_additional_security_headers


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Configurar logging estruturado
configure_structured_logging(
    log_level=getattr(settings, 'LOG_LEVEL', 'INFO'),
    json_logs=settings.ENVIRONMENT == "production",
    development_mode=settings.ENVIRONMENT == "development"
)

logger = logging.getLogger(__name__)


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan_with_improvements(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação com melhorias."""
    logger.info("Starting application with improvements...")
    
    # Startup
    try:
        # Get required services from DI container
        tws_client = await app_container.get(ITWSClient)
        agent_manager = await app_container.get(IAgentManager)
        knowledge_graph = await app_container.get(IKnowledgeGraph)
        
        # Initialize TWS monitor
        from resync.core.tws_monitor import get_tws_monitor
        tws_monitor_instance = await get_tws_monitor(tws_client)
        
        # Setup dependency injection
        setup_dependencies(tws_client, agent_manager, knowledge_graph)
        
        # Initialize CQRS dispatcher
        initialize_dispatcher(tws_client, tws_monitor_instance)
        
        logger.info("Application startup completed successfully")
        
        yield  # Application runs here
        
    except Exception as e:
        logger.critical(
            "Failed to start application",
            error=str(e),
            exc_info=True
        )
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        
        try:
            from resync.core.tws_monitor import shutdown_tws_monitor
            await shutdown_tws_monitor()
            logger.info("Application shutdown completed successfully")
        except Exception as e:
            logger.error(
                "Error during shutdown",
                error=str(e),
                exc_info=True
            )


# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan_with_improvements,
    # Configurações adicionais
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/api/openapi.json" if settings.ENVIRONMENT != "production" else None,
)


# ============================================================================
# MIDDLEWARE CONFIGURATION
# ============================================================================

# Correlation ID Middleware (deve ser o primeiro)
app.add_middleware(CorrelationIdMiddleware)

# CORS and Security
configure_cors(app, settings)
configure_csp(app, settings)
add_additional_security_headers(app)

# Rate limiting
init_rate_limiter(app)

logger.info("Middleware configured successfully")


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

register_exception_handlers(app)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

inject_container(app)


# ============================================================================
# TEMPLATE ENGINE
# ============================================================================
from jinja2 import select_autoescape

jinja2_env = Environment(
    loader=FileSystemLoader(str(settings.BASE_DIR / "templates")),
    auto_reload=settings.ENVIRONMENT == "development",
    cache_size=400 if settings.ENVIRONMENT == "production" else 0,
    enable_async=True,
    autoescape=select_autoescape(enabled_extensions=('html', 'xml'), disabled_extensions=())
)

templates = Jinja2Templates(directory=str(settings.BASE_DIR / "templates"))
templates.env = jinja2_env


# ============================================================================
# ROUTERS
# ============================================================================

# API routers
app.include_router(api_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(rag_upload_router)
app.include_router(chat_router, prefix="/ws", tags=["WebSocket Chat"])
app.include_router(audit_router)
app.include_router(health_router)
app.include_router(config_router)
app.include_router(cors_monitor_router, prefix="/api/cors", tags=["CORS Monitoring"])
app.include_router(performance_router, prefix="/api/performance", tags=["Performance Monitoring"])
app.include_router(
    agents_router,
    prefix="/api/v1/agents",
    tags=["Agents"],
)

logger.info("Routers registered successfully")


# ============================================================================
# STATIC FILES
# ============================================================================

static_dir = settings.BASE_DIR / "static"
if static_dir.exists() and static_dir.is_dir():
    from starlette.staticfiles import StaticFiles as StarletteStaticFiles
    import hashlib
    import os

    class CachedStaticFiles(StarletteStaticFiles):
        """Static files com cache otimizado."""
        
        async def get_response(self, path: str, full_path: str):
            response = await super().get_response(path, full_path)
            if response.status_code == 200:
                cache_max_age = getattr(settings, "STATIC_CACHE_MAX_AGE", 3600)
                response.headers["Cache-Control"] = f"public, max-age={cache_max_age}"
                
                try:
                    stat_result = os.stat(full_path)
                    file_metadata = f"{stat_result.st_size}-{int(stat_result.st_mtime)}"
                    etag_value = f'"{hashlib.sha256(file_metadata.encode()).hexdigest()[:16]}"'
                    response.headers["ETag"] = etag_value
                except Exception:
                    response.headers["ETag"] = f'"{hash(full_path)}"'
            
            return response
    
    app.mount(
        "/static",
        CachedStaticFiles(directory=static_dir),
        name="static",
    )
    logger.info(f"Mounted static directory at: {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")


# ============================================================================
# FRONTEND ENDPOINTS
# ============================================================================

@app.get("/revisao", response_class=HTMLResponse, tags=["Frontend"])
@dashboard_rate_limit
async def get_review_page(request: Request) -> HTMLResponse:
    """Serves the Human Review Dashboard."""
    return templates.TemplateResponse("revisao.html", {"request": request})


@app.get("/", include_in_schema=False)
async def root():
    """Redirects root to login page."""
    return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# CSP VIOLATION REPORT
# ============================================================================

@app.post("/csp-violation-report", include_in_schema=False)
async def csp_violation_report(request: Request):
    """Handle CSP violation reports."""
    try:
        body = await request.body()
        logger.warning(
            "CSP violation reported",
            violation=body.decode('utf-8', errors='ignore')
        )
        return JSONResponse(content={"status": "received"}, status_code=200)
    except Exception as e:
        logger.error(
            "Error processing CSP violation report",
            error=str(e),
            exc_info=True
        )
        return JSONResponse(content={"error": "processing failed"}, status_code=500)


# ============================================================================
# SETTINGS VALIDATION
# ============================================================================

def validate_settings():
    """Validate critical settings at startup."""
    validations = []
    
    # WebSocket settings
    if not hasattr(settings, 'WS_MAX_CONNECTION_DURATION'):
        validations.append("WS_MAX_CONNECTION_DURATION not set, using default")
    
    # Template cache
    if not hasattr(settings, 'JINJA2_TEMPLATE_CACHE_SIZE'):
        validations.append("JINJA2_TEMPLATE_CACHE_SIZE not set, using default")
    
    # Redis pool
    redis_max_size = getattr(settings, "REDIS_POOL_MAX_SIZE", 20)
    redis_min_size = getattr(settings, "REDIS_POOL_MIN_SIZE", 5)
    
    if redis_min_size > redis_max_size:
        logger.error(
            "Invalid Redis pool configuration",
            min_size=redis_min_size,
            max_size=redis_max_size
        )
        raise ValueError("REDIS_POOL_MIN_SIZE cannot be greater than REDIS_POOL_MAX_SIZE")
    
    # Log warnings
    for validation in validations:
        logger.warning(validation)
    
    logger.info("Settings validation completed")


# Validate settings
validate_settings()


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=getattr(settings, 'server_host', '127.0.0.1'),
        port=getattr(settings, 'server_port', 8000),
        log_config=None  # Usar nosso logging estruturado
    )
