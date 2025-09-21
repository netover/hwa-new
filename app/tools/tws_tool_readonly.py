import asyncio
from typing import Any, Dict, Optional

from agno.tools.toolkit import Toolkit

from app.core.config import settings


class TWSToolReadOnly(Toolkit):
    def __init__(self) -> None:
        super().__init__(name="tws_readonly")
        self.mock: bool = settings.TWS_MOCK_MODE
        self.session_token: Optional[str] = None

        if self.mock:
            print("🔧 TWSToolReadOnly operando em MODO MOCK.")
        else:
            print("⚡ TWSToolReadOnly operando em MODO REAL.")

    async def run(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        allowed_operations = {
            "get_job_status",
            "get_jobstream_status",
            "get_engine_status",
            "get_system_status",
            "get_job_history",
            "get_job_output",
            "search_jobs",
        }

        if operation not in allowed_operations:
            return {
                "error": "OPERAÇÃO BLOQUEADA",
                "details": f"A operação '{operation}' não é permitida. Apenas operações de leitura são ativadas.",
            }

        if self.mock:
            return await self._mock_response(operation, **kwargs)

        # Lógica para chamadas reais na API TWS
        if not self.session_token:
            await self._authenticate()

        return await self._execute_readonly(operation, **kwargs)

    async def _authenticate(self) -> Dict[str, str]:
        # Esta é uma implementação de mock/placeholder.
        # A lógica real de autenticação com a API TWS deve ser implementada aqui.
        print("Authenticating with TWS API (real)...")
        self.session_token = "real-token-placeholder"  # O token seria obtido da API
        return {"status": "authenticated"}

    async def _execute_readonly(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        # Esta é uma implementação de mock/placeholder.
        # A lógica real para executar as chamadas GET na API TWS seria implementada aqui,
        # possivelmente usando um cliente HTTP como o httpx.
        print(f"Executing REAL operation: {operation} with args: {kwargs}")
        return {"mock": False, "operation": operation, "data": "dados da API real aqui"}

    async def _mock_response(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        # Respostas simuladas para um ambiente de desenvolvimento/teste.
        await asyncio.sleep(0.1)  # Simula latência de rede

        if operation == "get_job_status":
            return {
                "jobs_found": 2,
                "jobs": [
                    {
                        "name": "JOB_A01_SUCCESS",
                        "status": "SUCC",
                        "workstation": "CPU_MASTER",
                    },
                    {
                        "name": "JOB_B02_RUNNING",
                        "status": "EXEC",
                        "workstation": "CPU_AGENT_01",
                    },
                ],
            }
        elif operation == "get_system_status":
            return {"status": "ACTIVE", "version": "10.1"}
        elif operation == "get_engine_status":
            return {
                "engines_found": 2,
                "engines": [
                    {"name": "CPU_MASTER", "status": "LINKED", "type": "master"},
                    {"name": "CPU_AGENT_01", "status": "LINKED", "type": "agent"},
                ],
            }
        else:
            return {"mock": True, "operation": operation, "args": kwargs}
