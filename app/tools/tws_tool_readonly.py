import asyncio
from typing import Any, Dict, Optional

from agno.tools.toolkit import Toolkit

from app.core.config import settings
from app.services.tws_client import OptimizedTWSClient


class TWSToolReadOnly(Toolkit):
    def __init__(self) -> None:
        super().__init__(name="tws_readonly")
        self.mock: bool = settings.TWS_MOCK_MODE

        # Apenas inicializa o cliente real se não estiver em modo mock
        self.client: Optional[OptimizedTWSClient] = None
        if not self.mock:
            self.client = OptimizedTWSClient()
            print("⚡ TWSToolReadOnly operando em MODO REAL com cliente otimizado.")
        else:
            print("🔧 TWSToolReadOnly operando em MODO MOCK.")

    async def run(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        allowed_operations = {
            "get_job_status", "get_jobstream_status", "get_engine_status",
            "get_system_status", "get_job_history", "get_job_output", "search_jobs"
        }

        if operation not in allowed_operations:
            return {
                "error": "OPERAÇÃO BLOQUEADA",
                "details": f"A operação '{operation}' não é permitida. Apenas operações de leitura são ativadas.",
            }

        if self.mock or not self.client:
            return await self._mock_response(operation, **kwargs)

        return await self._execute_readonly(operation, **kwargs)

    async def _execute_readonly(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Executa uma operação de leitura na API TWS usando os métodos
        específicos e cacheados do cliente otimizado.
        """
        if not self.client:
            return {"error": "Cliente TWS não inicializado. Verifique se não está em modo mock."}

        try:
            if operation == "get_job_status":
                return await self.client.get_job_status(**kwargs)
            elif operation == "get_system_status":
                return await self.client.get_system_status()
            elif operation == "get_engine_status":
                return await self.client.get_engine_status()
            else:
                # Fallback para operações não cacheadas ou mais genéricas
                return {"error": f"A operação real para '{operation}' não está implementada."}
        except Exception as e:
            print(f"❌ Erro ao executar operação '{operation}': {e}")
            return {"error": str(e)}

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
