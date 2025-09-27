# Resync Integration Guide

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration](#configuration)
3. [API Integration](#api-integration)
4. [WebSocket Integration](#websocket-integration)
5. [File Processing](#file-processing)
6. [Monitoring](#monitoring)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd resync

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration
```

### 2. Configuration

Create `agents.json`:

```json
{
  "agents": [
    {
      "id": "tws-specialist",
      "name": "TWS Specialist",
      "role": "TWS Environment Expert",
      "goal": "Help with TWS troubleshooting and monitoring",
      "backstory": "Expert in TWS operations and job scheduling",
      "tools": ["tws_status_tool", "tws_troubleshooting_tool"],
      "model_name": "llama3:latest",
      "memory": true,
      "verbose": false
    }
  ]
}
```

### 3. Start the Application

```bash
# Development
uvicorn resync.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn resync.main:app --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

```bash
# Application
APP_ENV=development
PROJECT_NAME=Resync
PROJECT_VERSION=0.1.0

# TWS Configuration
TWS_HOST=your-tws-host
TWS_PORT=31116
TWS_USER=your-username
TWS_PASSWORD=your-password
TWS_ENGINE_NAME=tws-engine
TWS_ENGINE_OWNER=tws-owner
TWS_MOCK_MODE=false
TWS_CACHE_TTL=300

# Knowledge Graph
MEM0_STORAGE_HOST=localhost
MEM0_STORAGE_PORT=6333
MEM0_EMBEDDING_PROVIDER=openai
MEM0_EMBEDDING_MODEL=text-embedding-3-small
MEM0_LLM_PROVIDER=openai
MEM0_LLM_MODEL=gpt-4o-mini

# File Processing
RAG_DIRECTORY=rag
```

### Agent Configuration

```json
{
  "agents": [
    {
      "id": "agent-id",
      "name": "Agent Name",
      "role": "Agent Role",
      "goal": "Agent Goal",
      "backstory": "Agent Backstory",
      "tools": ["tool1", "tool2"],
      "model_name": "llama3:latest",
      "memory": true,
      "verbose": false
    }
  ]
}
```

## API Integration

### REST API Client

```python
import httpx
import asyncio

class ResyncClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def get_agents(self):
        response = await self.client.get(f"{self.base_url}/api/agents")
        return response.json()
    
    async def get_status(self):
        response = await self.client.get(f"{self.base_url}/api/status")
        return response.json()
    
    async def get_health(self):
        response = await self.client.get(f"{self.base_url}/api/health/app")
        return response.json()
    
    async def close(self):
        await self.client.aclose()

# Usage
async def main():
    client = ResyncClient()
    try:
        agents = await client.get_agents()
        status = await client.get_status()
        print(f"Agents: {len(agents)}")
        print(f"Workstations: {len(status['workstations'])}")
    finally:
        await client.close()

asyncio.run(main())
```

### cURL Examples

```bash
# Get agents
curl -X GET "http://localhost:8000/api/agents"

# Get TWS status
curl -X GET "http://localhost:8000/api/status"

# Get health
curl -X GET "http://localhost:8000/api/health/app"

# Get metrics
curl -X GET "http://localhost:8000/api/metrics"
```

## WebSocket Integration

### Python WebSocket Client

```python
import asyncio
import websockets
import json

class ResyncChat:
    def __init__(self, agent_id: str, base_url: str = "ws://localhost:8000"):
        self.agent_id = agent_id
        self.uri = f"{base_url}/ws/{agent_id}"
        self.websocket = None
    
    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
    
    async def send_message(self, message: str):
        await self.websocket.send(message)
    
    async def receive_response(self):
        response = ""
        async for message in self.websocket:
            data = json.loads(message)
            if data['type'] == 'stream':
                response += data['message']
            elif data.get('is_final'):
                response += data['message']
                break
        return response
    
    async def close(self):
        if self.websocket:
            await self.websocket.close()

# Usage
async def chat_example():
    chat = ResyncChat("tws-specialist")
    try:
        await chat.connect()
        await chat.send_message("What's the status of the TWS system?")
        response = await chat.receive_response()
        print(f"Agent: {response}")
    finally:
        await chat.close()

asyncio.run(chat_example())
```

### JavaScript WebSocket Client

```javascript
class ResyncChat {
    constructor(agentId, baseUrl = 'ws://localhost:8000') {
        this.agentId = agentId;
        this.ws = null;
        this.baseUrl = baseUrl;
    }
    
    connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(`${this.baseUrl}/ws/${this.agentId}`);
            
            this.ws.onopen = () => {
                console.log('Connected to agent');
                resolve();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                reject(error);
            };
        });
    }
    
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        }
    }
    
    onMessage(callback) {
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            callback(data);
        };
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Usage
const chat = new ResyncChat('tws-specialist');
chat.connect().then(() => {
    chat.sendMessage("What's the status?");
    chat.onMessage((data) => {
        console.log(`${data.sender}: ${data.message}`);
    });
});
```

## File Processing

### File Upload

```python
import httpx
import asyncio

async def upload_file(file_path: str):
    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = await client.post(
                "http://localhost:8000/api/rag/upload",
                files=files
            )
            return response.json()

# Usage
result = await upload_file("document.pdf")
print(f"Uploaded: {result['filename']}")
```

### Batch Upload

```python
import asyncio
import httpx
from pathlib import Path

async def upload_multiple_files(file_paths: list):
    async with httpx.AsyncClient() as client:
        tasks = []
        for file_path in file_paths:
            task = upload_single_file(client, file_path)
            tasks.append(task)
        return await asyncio.gather(*tasks)

async def upload_single_file(client: httpx.AsyncClient, file_path: str):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = await client.post(
            "http://localhost:8000/api/rag/upload",
            files=files
        )
        return response.json()

# Usage
file_paths = ["doc1.pdf", "doc2.docx", "doc3.xlsx"]
results = await upload_multiple_files(file_paths)
for result in results:
    print(f"Uploaded: {result['filename']}")
```

## Monitoring

### Health Monitoring

```python
import asyncio
import httpx
from datetime import datetime

class ResyncMonitor:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def check_health(self):
        try:
            # Check app health
            app_health = await self.client.get(f"{self.base_url}/api/health/app")
            
            # Check TWS health
            tws_health = await self.client.get(f"{self.base_url}/api/health/tws")
            
            # Get status
            status = await self.client.get(f"{self.base_url}/api/status")
            
            return {
                "timestamp": datetime.now().isoformat(),
                "app_health": app_health.json(),
                "tws_health": tws_health.json(),
                "status": status.json()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def monitor_continuously(self, interval: int = 60):
        while True:
            health = await self.check_health()
            print(f"{health['timestamp']}: {health}")
            await asyncio.sleep(interval)
    
    async def close(self):
        await self.client.aclose()

# Usage
async def main():
    monitor = ResyncMonitor()
    try:
        await monitor.monitor_continuously(interval=30)
    except KeyboardInterrupt:
        print("Monitoring stopped")
    finally:
        await monitor.close()

asyncio.run(main())
```

### Metrics Collection

```python
import asyncio
import httpx

async def collect_metrics():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/metrics")
        return response.text

# Usage
metrics = await collect_metrics()
print(metrics)
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "resync.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  resync:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TWS_HOST=your-tws-host
      - TWS_PORT=31116
      - TWS_USER=your-username
      - TWS_PASSWORD=your-password
    volumes:
      - ./agents.json:/app/agents.json
      - ./rag:/app/rag
    depends_on:
      - redis
      - qdrant

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
```

### Production Configuration

```python
# config/production.py
from pydantic_settings import BaseSettings

class ProductionSettings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Resync"
    PROJECT_VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI-powered TWS management system"
    
    # TWS Configuration
    TWS_HOST: str
    TWS_PORT: int = 31116
    TWS_USER: str
    TWS_PASSWORD: str
    TWS_ENGINE_NAME: str = "tws-engine"
    TWS_ENGINE_OWNER: str = "tws-owner"
    TWS_MOCK_MODE: bool = False
    TWS_CACHE_TTL: int = 300
    
    # Knowledge Graph
    MEM0_STORAGE_HOST: str = "qdrant"
    MEM0_STORAGE_PORT: int = 6333
    MEM0_EMBEDDING_PROVIDER: str = "openai"
    MEM0_EMBEDDING_MODEL: str = "text-embedding-3-small"
    MEM0_LLM_PROVIDER: str = "openai"
    MEM0_LLM_MODEL: str = "gpt-4o-mini"
    
    # File Processing
    RAG_DIRECTORY: str = "rag"
    
    # Agent Configuration
    AGENT_CONFIG_PATH: str = "agents.json"
    
    class Config:
        env_file = ".env"
```

## Troubleshooting

### Common Issues

#### 1. Connection Errors

```python
# Check TWS connection
async def check_tws_connection():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/health/tws")
            if response.status_code == 200:
                print("TWS connection OK")
            else:
                print(f"TWS connection failed: {response.status_code}")
        except Exception as e:
            print(f"TWS connection error: {e}")
```

#### 2. WebSocket Connection Issues

```python
# Test WebSocket connection
async def test_websocket():
    try:
        async with websockets.connect("ws://localhost:8000/ws/tws-specialist") as ws:
            await ws.send("test")
            response = await ws.recv()
            print(f"WebSocket OK: {response}")
    except Exception as e:
        print(f"WebSocket error: {e}")
```

#### 3. File Upload Issues

```python
# Test file upload
async def test_file_upload():
    async with httpx.AsyncClient() as client:
        try:
            with open("test.txt", "w") as f:
                f.write("test content")
            
            with open("test.txt", "rb") as f:
                files = {"file": f}
                response = await client.post(
                    "http://localhost:8000/api/rag/upload",
                    files=files
                )
                print(f"Upload result: {response.json()}")
        except Exception as e:
            print(f"Upload error: {e}")
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug
uvicorn resync.main:app --reload --log-level debug
```

### Performance Monitoring

```python
import time
import asyncio

async def benchmark_api():
    async with httpx.AsyncClient() as client:
        start_time = time.time()
        
        # Test multiple endpoints
        tasks = [
            client.get("http://localhost:8000/api/agents"),
            client.get("http://localhost:8000/api/status"),
            client.get("http://localhost:8000/api/health/app")
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        print(f"API benchmark: {end_time - start_time:.2f}s")
        for i, result in enumerate(results):
            print(f"Endpoint {i}: {result.status_code}")

asyncio.run(benchmark_api())
```

This integration guide provides comprehensive information for integrating with the Resync system, from basic setup to advanced monitoring and troubleshooting.