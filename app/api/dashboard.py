import asyncio
import json
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse

from app.tools.tws_tool_readonly import TWSToolReadOnly

router = APIRouter(prefix="/api/dashboard")
tws_reader = TWSToolReadOnly()


class ConnectionManager:
    """Gerencia conexões WebSocket e a tarefa de monitoramento do dashboard."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        self._monitor_task: asyncio.Task[None] | None = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        if not self._monitor_task or self._monitor_task.done():
            print("🚀 Iniciando monitor do dashboard (primeiro cliente conectado).")
            self._monitor_task = asyncio.create_task(self._monitor_loop())

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if not self.active_connections and self._monitor_task:
            print("🛑 Parando monitor do dashboard (último cliente desconectado).")
            self._monitor_task.cancel()
            self._monitor_task = None

    async def _broadcast(self, data: Dict[str, Any]) -> None:
        message = json.dumps(data)
        for connection in self.active_connections[:]:  # Itera sobre uma cópia
            try:
                await connection.send_text(message)
            except (WebSocketDisconnect, RuntimeError):
                self.disconnect(connection)

    async def _monitor_loop(self) -> None:
        while self.active_connections:
            try:
                data = await self._collect_dashboard_data()
                await self._broadcast(data)
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                print("Monitor do dashboard cancelado.")
                break
            except Exception as e:
                print(f"❌ Erro no loop de monitoramento: {e}")
                await asyncio.sleep(15)  # Espera mais em caso de erro
        print("Loop de monitoramento encerrado.")
        self._monitor_task = None

    async def _collect_dashboard_data(self) -> Dict[str, Any]:
        """Coleta dados do dashboard de forma concorrente."""
        system_task = tws_reader.run("get_system_status")
        engines_task = tws_reader.run("get_engine_status")
        jobs_task = tws_reader.run("get_job_status")

        # Executa as chamadas em paralelo para maior eficiência
        results = await asyncio.gather(
            system_task, engines_task, jobs_task, return_exceptions=True
        )

        system, engines, jobs = results

        return {
            "type": "dashboard_update",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "system": (
                    system
                    if not isinstance(system, Exception)
                    else {"error": str(system)}
                ),
                "engines": (
                    engines
                    if not isinstance(engines, Exception)
                    else {"error": str(engines)}
                ),
                "jobs": (
                    jobs if not isinstance(jobs, Exception) else {"error": str(jobs)}
                ),
            },
        }


manager = ConnectionManager()


@router.websocket("/ws")  # type: ignore[misc]
async def dashboard_ws(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        # Mantém a conexão viva, aguardando mensagens do cliente (que não são usadas aqui)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/stream")  # type: ignore[misc]
async def dashboard_sse(request: Request) -> EventSourceResponse:
    """Endpoint SSE para atualizações do dashboard."""

    async def event_generator() -> AsyncGenerator[Dict[str, Any], None]:
        while True:
            if await request.is_disconnected():
                break
            data = await manager._collect_dashboard_data()
            yield {
                "event": "dashboard_update",
                "data": json.dumps(data),
                "retry": 5000,
            }
            await asyncio.sleep(5)

    return EventSourceResponse(event_generator())


@router.get("/snapshot")  # type: ignore[misc]
async def dashboard_snapshot() -> Dict[str, Any]:
    """Endpoint para obter um snapshot único dos dados do dashboard."""
    return await manager._collect_dashboard_data()
