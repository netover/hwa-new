import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from app.core.logging import log_json


class ModelInfo(BaseModel):  # type: ignore[misc]
    id: str
    name: str
    created: Optional[int] = None
    context_length: int
    pricing: Dict[str, float]
    top_provider: Dict[str, Any] = {}


class ModelDiscoveryService:
    def __init__(self) -> None:
        self.cache: Dict[str, ModelInfo] = {}
        self.last_fetch: Optional[datetime] = None
        self.cache_ttl: timedelta = timedelta(hours=1)

    async def get_available_models(
        self, force_refresh: bool = False
    ) -> List[ModelInfo]:
        now = datetime.now()
        if (
            not force_refresh
            and self.cache
            and self.last_fetch
            and now - self.last_fetch < self.cache_ttl
        ):
            return list(self.cache.values())

        url = "https://openrouter.ai/api/v1/models"
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            log_json(
                {
                    "level": "WARNING",
                    "message": "OPENROUTER_API_KEY não configurada. Usando modelos de fallback.",
                    "service": "ModelDiscovery",
                }
            )
            self.cache = self._fallback_models()
            return list(self.cache.values())

        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:8000",  # Referer pode ser customizável
            "X-Title": "Resync Dashboard",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()  # Lança exceção para status 4xx/5xx

                models_data = response.json().get("data", [])
                self.cache.clear()
                for m in models_data:
                    model_obj = ModelInfo(
                        id=m["id"],
                        name=m.get("name", m["id"]),
                        created=m.get("created"),
                        context_length=m.get("context_length", 4096),
                        pricing=m.get("pricing", {"prompt": 0.0, "completion": 0.0}),
                        top_provider=m.get("top_provider", {}),
                    )
                    self.cache[model_obj.id] = model_obj

                self.last_fetch = now
                log_json(
                    {
                        "level": "INFO",
                        "message": f"Modelos do OpenRouter carregados com sucesso: {len(self.cache)}",
                        "service": "ModelDiscovery",
                    }
                )

        except httpx.RequestError as e:
            log_json(
                {
                    "level": "ERROR",
                    "message": f"Erro de rede ao buscar modelos do OpenRouter. Usando fallback. Erro: {e}",
                    "service": "ModelDiscovery",
                }
            )
            self.cache = self._fallback_models()
        except Exception as e:
            log_json(
                {
                    "level": "ERROR",
                    "message": f"Erro inesperado ao processar modelos. Usando fallback. Erro: {e}",
                    "service": "ModelDiscovery",
                }
            )
            self.cache = self._fallback_models()

        return list(self.cache.values())

    def _fallback_models(self) -> Dict[str, ModelInfo]:
        return {
            "openrouter/auto": ModelInfo(
                id="openrouter/auto",
                name="Auto (melhor modelo)",
                context_length=128000,
                pricing={"prompt": 0.0, "completion": 0.0},
                top_provider={},
            ),
            "openai/gpt-4o": ModelInfo(
                id="openai/gpt-4o",
                name="GPT-4 O",
                context_length=128000,
                pricing={"prompt": 0.005, "completion": 0.015},
                top_provider={"name": "OpenAI"},
            ),
        }

    async def validate_model(self, model_id: str) -> Optional[ModelInfo]:
        await self.get_available_models()
        return self.cache.get(model_id)

    async def suggest_models(self, q: str) -> List[ModelInfo]:
        await self.get_available_models()
        q_lower = q.lower()
        return [
            m
            for m in self.cache.values()
            if q_lower in m.id.lower() or q_lower in m.name.lower()
        ][:10]


model_discovery = ModelDiscoveryService()
