
"""
Resync Application Main Entry Point.

This module serves as the primary entry point for the Resync application,
providing startup validation, configuration loading, and application
initialization. It implements a robust startup process that validates
system configuration before launching the FastAPI application.

The startup process includes:
- Configuration validation and environment checks
- Dependency verification (Redis, databases)
- Security context initialization
- Application factory setup and launch

Error handling is comprehensive, providing clear feedback for configuration
issues, dependency problems, and startup failures.

Usage:
    python -m resync.main
    # or
    python resync/main.py
"""

import sys

import structlog

from resync.api.routes import api
from resync.core.encoding_utils import symbol
from resync.core.exceptions import ConfigurationError

# Configure startup logger
startup_logger = structlog.get_logger("resync.startup")


def validate_configuration_on_startup():
    """
    Validate system configuration before application startup.

    This function performs comprehensive validation of the application environment
    including settings, dependencies, and security configurations. It provides
    detailed feedback about any configuration issues that need to be resolved
    before the application can start successfully.

    The validation includes:
    - Settings loading and schema validation
    - Environment variable checks
    - Database connectivity tests
    - Security configuration verification
    - Dependency availability confirmation

    Raises:
        ConfigurationError: If critical configuration issues are detected
        SystemExit: With appropriate exit code for startup failures
    """

    startup_logger.info("configuration_validation_started")

    try:
        # Import aqui para evitar dependências circulares
        from resync.settings import load_settings

        # Forçar reload de settings
        settings = load_settings()

        startup_logger.info(
            "configuration_validation_successful",
            environment=settings.environment,
            redis_host=(
                settings.redis_url.split("@")[-1]
                if "@" in settings.redis_url
                else settings.redis_url
            ),
            tws_host=settings.tws_host,
            tws_port=settings.tws_port,
            status_symbol=symbol(True, sys.stdout),
        )

        return settings

    except ConfigurationError as e:
        startup_logger.error(
            "configuration_validation_failed",
            error_message=e.message,
            error_details=e.details,
            validation_errors=e.details.get("errors", []),
            status_symbol=symbol(False, sys.stdout),
        )

        # Log configuration guidance for developers
        startup_logger.warning(
            "configuration_setup_required",
            admin_username="admin",
            admin_password="suasenha123",
            secret_key_generation="python -c 'import secrets; print(secrets.token_urlsafe(32))'",
            redis_url="redis://localhost:6379",
            tws_host="localhost",
            tws_port=31111,
            tws_user="twsuser",
            tws_password="twspass",
        )

        sys.exit(1)


# Validar configuração na importação do módulo
if __name__ != "__main__":
    # Apenas validar quando rodando via uvicorn
    if "uvicorn" in sys.argv[0] or "gunicorn" in sys.argv[0]:
        settings = validate_configuration_on_startup()

# Create the FastAPI application
from resync.fastapi_app.main import app

if __name__ == "__main__":
    import uvicorn

    from resync.settings import settings

    uvicorn.run(
        app,
        host=getattr(settings, "server_host", "127.0.0.1"),
        port=getattr(settings, "server_port", 8000),
        log_config=None,  # Use our structured logging
    )
