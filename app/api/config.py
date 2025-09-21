import json
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException

# Importa a instância 'reg' e a renomeia para consistência
from app.agents.manager import reg as agent_manager

router = APIRouter(prefix="/api/config", tags=["Configuration"])


@router.post(  # type: ignore[misc]
    "/reload",
    summary="Recarregar a configuração dos agentes",
    description="Força o recarregamento da configuração dos agentes a partir do arquivo 'runtime.json'.",
)
async def force_reload_config() -> Dict[str, str]:
    config_path = Path("config/runtime.json")

    if not config_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Arquivo de configuração '{config_path}' não encontrado.",
        )

    try:
        new_config = json.loads(config_path.read_text())

        # Acessa o método do gerenciador de agentes para recarregar
        await agent_manager.reload_agents_from_file(new_config)

        return {
            "status": "success",
            "message": "Configuração e agentes recarregados com sucesso.",
        }

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro de formatação no arquivo JSON '{config_path}': {e}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao recarregar a configuração dos agentes: {e}",
        ) from e
