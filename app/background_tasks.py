import asyncio
from typing import NoReturn

from app.services.model_discovery import model_discovery


async def periodic_model_refresh() -> NoReturn:
    while True:
        try:
            await asyncio.sleep(86400)  # 24 horas
            print("🔄 Auto-refresh diário de modelos OpenRouter")
            await model_discovery.get_available_models(force_refresh=True)
        except Exception as e:
            print(f"❌ Erro no refresh automático: {e}")
