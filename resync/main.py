"""Main application entry point."""

import sys
from resync.app_factory import create_app
from resync.core.exceptions import ConfigurationError


def validate_configuration_on_startup():
    """Valida configuração antes de iniciar aplicação."""

    print("\n🔍 Validando configuração...")

    try:
        # Import aqui para evitar dependências circulares
        from resync.settings import load_settings

        # Forçar reload de settings
        settings = load_settings()

        print("✅ Configuração válida!")
        print(f"   Ambiente: {settings.environment}")
        print(f"   Redis: {settings.redis_url.split('@')[-1]}")
        print(f"   TWS: {settings.tws_host}:{settings.tws_port}")
        print()

        return settings

    except ConfigurationError as e:
        print(f"\n❌ ERRO DE CONFIGURAÇÃO:")
        print(f"   {e.message}")

        if e.details.get("errors"):
            print("\n   Erros encontrados:")
            for error in e.details["errors"]:
                if error.strip():
                    print(f"   • {error}")

        print("\n   Crie um arquivo .env na raiz do projeto com:")
        print("   ADMIN_USERNAME=admin")
        print("   ADMIN_PASSWORD=suasenha123")
        print("   SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')")
        print("   REDIS_URL=redis://localhost:6379")
        print("   TWS_HOST=localhost")
        print("   TWS_PORT=31111")
        print("   TWS_USER=twsuser")
        print("   TWS_PASSWORD=twspass")
        print()

        sys.exit(1)


# Validar configuração na importação do módulo
if __name__ != "__main__":
    # Apenas validar quando rodando via uvicorn
    if "uvicorn" in sys.argv[0] or "gunicorn" in sys.argv[0]:
        settings = validate_configuration_on_startup()

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    from resync.settings import settings
    
    uvicorn.run(
        app,
        host=getattr(settings, 'server_host', '127.0.0.1'),
        port=getattr(settings, 'server_port', 8000),
        log_config=None  # Use our structured logging
    )
