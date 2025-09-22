import asyncio
from typing import Any, Dict

import httpx

from app.core.caching import cache_response
from app.core.config import settings


class OptimizedTWSClient:
    """
    Um cliente HTTP otimizado para fazer requisições à API do TWS,
    com connection pooling, timeouts e retries.
    """
    def __init__(self) -> None:
        self.base_url = settings.TWS_HOST
        limits = httpx.Limits(
            max_keepalive_connections=10,
            max_connections=20,
            keepalive_expiry=30.0
        )
        timeout = httpx.Timeout(
            connect=5.0,
            read=30.0,
            write=5.0,
            pool=2.0
        )
        self.client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            http2=True,
            verify=False,  # Comum para ambientes TWS com certificados autoassinados
            headers={
                'User-Agent': 'Resync-HWA-Dashboard/1.0',
                'Accept': 'application/json',
            }
        )

    async def close(self) -> None:
        """Fecha o cliente HTTP de forma segura."""
        if self.client:
            await self.client.aclose()

    async def make_request(self, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Executa uma requisição para a API TWS com lógica de retry.
        """
        auth = (settings.TWS_USERNAME, settings.TWS_PASSWORD)
        url = f"{self.base_url}{endpoint}"

        for attempt in range(3):  # Tenta até 3 vezes
            try:
                response = await self.client.get(url, auth=auth, **kwargs)
                response.raise_for_status()  # Lança exceção para status 4xx/5xx
                return response.json()  # A biblioteca httpx já retorna um Dict[str, Any] ou List[Any]

            except httpx.TimeoutException as e:
                print(f"⚠️  Timeout na tentativa {attempt + 1} para {url}: {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff: 1, 2, 4s

            except httpx.HTTPStatusError as e:
                # Retry apenas para erros de servidor (5xx)
                if e.response.status_code >= 500 and attempt < 2:
                    print(f"⚠️  Erro de servidor {e.response.status_code} na tentativa {attempt + 1}. Tentando novamente...")
                    await asyncio.sleep(2 ** attempt)
                else:
                    # Não tenta novamente para erros de cliente (4xx) ou na última tentativa
                    print(f"❌ Erro HTTP {e.response.status_code} não recuperável para {url}.")
                    raise

        # Este ponto não deveria ser alcançado, mas garante que a função sempre retorne ou levante erro.
        raise Exception("Falha na requisição após múltiplas tentativas.")

    async def __aenter__(self) -> "OptimizedTWSClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    # --- Métodos de Consulta Específicos com Cache ---

    @cache_response(ttl_seconds=30)
    async def get_system_status(self) -> Dict[str, Any]:
        """Busca o status geral do sistema."""
        return await self.make_request("/system/status")

    @cache_response(ttl_seconds=15)
    async def get_engine_status(self) -> Dict[str, Any]:
        """Busca o status de todos os motores."""
        return await self.make_request("/engine/status")

    @cache_response(ttl_seconds=10)
    async def get_job_status(self, **kwargs: Any) -> Dict[str, Any]:
        """Busca o status de um ou mais jobs, com base nos filtros."""
        return await self.make_request("/plan/job", params=kwargs)
