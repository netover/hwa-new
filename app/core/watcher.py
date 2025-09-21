import asyncio
import json
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict

from watchfiles import awatch

# Removido: from app.agents.manager import agent_manager
# Isso quebra a dependência circular.


async def watch_config_and_reload(
    config_path: Path, reload_callback: Callable[[Dict[str, Any]], Awaitable[None]]
) -> None:
    """
    Observa o arquivo de configuração e chama o callback de recarregamento quando ele muda.

    Args:
        config_path: O caminho para o arquivo de configuração (runtime.json).
        reload_callback: A função assíncrona a ser chamada com a nova configuração.
    """
    while True:
        # awatch retorna um set de tuplas (change, path)
        async for changes in awatch(str(config_path.parent)):
            # Verificamos se o nosso arquivo de configuração específico está entre as mudanças
            if any(Path(path) == config_path for _, path in changes):
                print(f"🔄 Configuração em '{config_path}' alterada. Recarregando...")
                try:
                    new_cfg = json.loads(config_path.read_text())
                    await reload_callback(new_cfg)
                except json.JSONDecodeError as e:
                    print(f"❌ Erro ao decodificar JSON em '{config_path}': {e}")
                except Exception as e:
                    print(f"❌ Erro inesperado ao recarregar configuração: {e}")

        # O awatch bloqueia até que haja uma mudança, mas um pequeno sleep pode ser
        # prudente em um loop `while True` caso o awatch saia inesperadamente.
        await asyncio.sleep(1)
