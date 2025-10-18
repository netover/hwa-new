
"""
FastAPI Application Main Entry Point
"""
from fastapi import FastAPI, WebSocket
from .api.v1.routes.auth import router as auth_router
from .api.v1.routes.chat import router as chat_router
from .api.v1.routes.audit import router as audit_router
from .api.v1.routes.agents import router as agents_router
from .api.v1.routes.rag import router as rag_router
from .api.v1.routes.status import router as status_router
from .api.websocket.handlers import websocket_handler

app = FastAPI(
    title="HWA API",
    version="1.0",
    description="High-Performance Web Application API"
)

# Include routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(audit_router, prefix="/api", tags=["Audit"])
app.include_router(agents_router, prefix="/api", tags=["Agents"])
app.include_router(rag_router, prefix="/api", tags=["RAG"])
app.include_router(status_router, prefix="/api", tags=["Status"])

# WebSocket endpoint
@app.websocket("/api/v1/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time chat with agents"""
    await websocket_handler(websocket, agent_id)

@app.get("/")
async def root():
    return {"message": "HWA API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# API routes are now handled by routers included above
# Direct app routes removed to avoid conflicts
