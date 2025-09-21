import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import chat, config, dashboard, health, models
from app.core.config import settings

# --- Criação da Aplicação FastAPI ---
app = FastAPI(
    title="Resync - AI-Powered TWS Dashboard",
    version="1.0.0",
    description="Dashboard de monitoramento em tempo real para HCL Workload Automation (TWS) com IA.",
)


# --- Eventos de Ciclo de Vida (Startup/Shutdown) ---
@app.on_event("startup")  # type: ignore[misc]
async def startup_event() -> None:
    """Executa tarefas essenciais na inicialização da aplicação."""
    # Importa a instância do gerenciador de agentes
    from app.agents.manager import reg as agent_manager

    # Inicializa o gerenciador, que carrega os agentes e inicia o watcher de configuração.
    await agent_manager.initialize()

    # Inicia tarefas que rodam em background
    if settings.ENABLE_MODEL_DISCOVERY:
        from app.background_tasks import periodic_model_refresh

        asyncio.create_task(periodic_model_refresh())
        print("🔄 Tarefa de atualização periódica de modelos iniciada.")

    print("🚀 Resync backend iniciado com sucesso.")


@app.on_event("shutdown")  # type: ignore[misc]
async def shutdown_event() -> None:
    """Executa tarefas de limpeza no encerramento da aplicação."""
    print("🛑 Encerrando Resync backend.")
    # Futuramente, pode incluir o cancelamento de tarefas de background ou fechamento de conexões.


# --- Inclusão dos Roteadores da API ---
print("🔌 Montando roteadores da API...")
app.include_router(chat.router, tags=["Chat"])
app.include_router(config.router, tags=["Configuration"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(health.router, tags=["Health"])
app.include_router(models.router, tags=["LLM Models"])

# --- Montagem de Arquivos Estáticos (Frontend) ---
# Serve o arquivo index.html e os assets (CSS, JS)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

print("✅ Aplicação configurada e pronta para ser executada.")

# Para executar:
# uvicorn app.__main__:app --reload --host 0.0.0.0 --port 8000
