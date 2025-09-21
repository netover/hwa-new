import asyncio
from typing import NoReturn

from app.services.model_discovery import model_discovery


async def periodic_model_refresh() -> NoReturn:
    while True:
        try:
            await asyncio.sleep(3600)  # 1 hora
            print("🔄 Auto-refresh modelos OpenRouter")
            await model_discovery.get_available_models(force_refresh=True)
        except Exception as e:
            print(f"❌ Erro no refresh automático: {e}")
