# Resync API Documentation

## Table of Contents

1. [Overview](#overview)
2. [API Endpoints](#api-endpoints)
3. [Core Components](#core-components)
4. [Data Models](#data-models)
5. [Services](#services)
6. [Tools](#tools)
7. [Usage Examples](#usage-examples)
8. [Integration Guide](#integration-guide)

## Overview

Resync is a comprehensive AI-powered system for managing and monitoring TWS (Tivoli Workload Scheduler) environments. It provides real-time chat interfaces with specialized AI agents, knowledge graph integration for continuous learning, and robust file processing capabilities.

### Key Features

- **AI Agent Management**: Dynamic agent creation and management with specialized tools
- **Real-time Chat**: WebSocket-based communication with AI agents
- **Knowledge Graph**: Persistent memory system using Mem0 AI for continuous learning
- **File Processing**: Support for PDF, DOCX, and Excel file ingestion
- **TWS Integration**: Direct integration with TWS environments
- **Audit System**: Human-in-the-loop review system for AI-generated content
- **Caching**: Multi-level caching system for optimal performance

## API Endpoints

### Main Application

#### `GET /`
- **Description**: Redirects to the main API documentation
- **Response**: 302 Redirect to `/api/docs`

#### `GET /revisao`
- **Description**: Serves the human review dashboard page
- **Response**: HTML page for the review interface

### Core API Endpoints

#### `GET /api/dashboard`
- **Description**: Serves the main dashboard interface
- **Response**: HTML content of the dashboard
- **Error**: 404 if dashboard file not found

#### `GET /api/agents`
- **Description**: Retrieves all agent configurations
- **Response Model**: `List[AgentConfig]`
- **Dependencies**: `IAgentManager`

**Example Response:**
```json
[
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
```

#### `GET /api/status`
- **Description**: Provides comprehensive TWS system status
- **Response Model**: `SystemStatus`
- **Dependencies**: `ITWSClient`

**Example Response:**
```json
{
  "workstations": [
    {
      "name": "WORKSTATION1",
      "status": "LINKED",
      "type": "FTA"
    }
  ],
  "jobs": [
    {
      "name": "JOB001",
      "workstation": "WORKSTATION1",
      "status": "SUCC",
      "job_stream": "STREAM1"
    }
  ],
  "critical_jobs": [
    {
      "job_id": 123,
      "job_name": "CRITICAL_JOB",
      "status": "RUNNING",
      "start_time": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### `GET /api/health/app`
- **Description**: Application health check
- **Response**: `{"status": "ok"}`

#### `GET /api/health/tws`
- **Description**: TWS connection health check
- **Response**: `{"status": "ok", "message": "Conexão com o TWS bem-sucedida."}`
- **Error**: 503 if TWS connection fails

#### `GET /api/metrics`
- **Description**: Application metrics in Prometheus format
- **Response**: Plain text metrics

### Chat Endpoints

#### `WebSocket /ws/{agent_id}`
- **Description**: Real-time chat with specific AI agents
- **Parameters**: 
  - `agent_id` (path): The ID of the agent to chat with
- **Dependencies**: `IAgentManager`, `IConnectionManager`, `IKnowledgeGraph`

**WebSocket Message Format:**
```json
{
  "type": "message|stream|error|info",
  "sender": "user|agent|system",
  "message": "Message content",
  "is_final": true  // Only for final agent responses
}
```

**Example Usage:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tws-specialist');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`${data.sender}: ${data.message}`);
};
```

### RAG Upload Endpoints

#### `POST /api/rag/upload`
- **Description**: Upload documents for RAG ingestion
- **Request**: Multipart form data with file
- **Response**: Upload confirmation with filename
- **Dependencies**: `IFileIngestor`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/rag/upload" \
  -F "file=@document.pdf"
```

**Example Response:**
```json
{
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "message": "File uploaded successfully and queued for ingestion."
}
```

### Audit Endpoints

#### `GET /api/audit/flags`
- **Description**: Retrieves flagged memories for human review
- **Query Parameters**:
  - `status`: Filter by audit status (pending, approved, rejected, all)
  - `query`: Search query in user_query or agent_response
- **Response Model**: `List[Dict[str, Any]]`
- **Dependencies**: `IAuditQueue`

#### `POST /api/audit/review`
- **Description**: Process human review actions for flagged memories
- **Request Model**: `ReviewAction`
- **Dependencies**: `IAuditQueue`, `IKnowledgeGraph`

**Example Request:**
```json
{
  "memory_id": "mem_123",
  "action": "approve"  // or "reject"
}
```

#### `GET /api/audit/metrics`
- **Description**: Returns audit queue metrics
- **Response Model**: `Dict[str, int]`
- **Dependencies**: `IAuditQueue`

### Security Testing Endpoints

#### `POST /api/chat`
- **Description**: Chat endpoint for testing input validation
- **Request**: `{"message": "string"}`
- **Response**: `{"response": "ok"}`
- **Security**: XSS detection and prevention

#### `POST /api/sensitive`
- **Description**: Sensitive endpoint for testing encryption
- **Request**: `{"data": "sensitive information"}`
- **Response**: `{"encrypted": "encrypted_data"}`

#### `GET /api/protected`
- **Description**: Protected endpoint for testing authentication
- **Response**: 401 Unauthorized

#### `GET /api/admin/users`
- **Description**: Admin endpoint for testing authorization
- **Response**: 403 Forbidden

#### `POST /api/review`
- **Description**: Review endpoint for testing input validation
- **Request Model**: `ReviewRequest`
- **Security**: XSS detection and prevention

#### `POST /api/execute`
- **Description**: Execute endpoint for testing input validation
- **Request Model**: `ExecuteRequest`
- **Security**: Command injection prevention

#### `GET /api/files/{path}`
- **Description**: Files endpoint for testing path traversal
- **Security**: Path traversal prevention

## Core Components

### AgentManager

The `AgentManager` class manages the lifecycle and operations of AI agents.

#### Key Methods

##### `async load_agents_from_config(config_path: Path = None) -> None`
- **Description**: Loads agent configurations from a JSON file
- **Parameters**: 
  - `config_path`: Optional path to configuration file
- **Raises**: `DataParsingError`, `MissingConfigError`, `ConfigError`, `InvalidConfigError`

##### `get_agent(agent_id: str) -> Optional[Any]`
- **Description**: Retrieves a loaded agent by its ID
- **Parameters**: `agent_id` - The ID of the agent to retrieve
- **Returns**: Agent instance or None if not found

##### `get_all_agents() -> List[AgentConfig]`
- **Description**: Returns the configuration of all loaded agents
- **Returns**: List of agent configurations

##### `get_agent_with_tool(agent_id: str, tool_name: str) -> Optional[Any]`
- **Description**: Retrieves an agent that has the specified tool
- **Parameters**:
  - `agent_id`: The ID of the agent
  - `tool_name`: The name of the required tool
- **Raises**: `ValueError` if agent or tool not found

### AsyncKnowledgeGraph

The `AsyncKnowledgeGraph` class manages persistent knowledge using Mem0 AI.

#### Key Methods

##### `async add_conversation(user_query: str, agent_response: str, agent_id: str, context: Optional[Dict[str, Any]] = None) -> str`
- **Description**: Stores a conversation in the knowledge graph
- **Parameters**:
  - `user_query`: The user's question or command
  - `agent_response`: The agent's response
  - `agent_id`: The ID of the agent that responded
  - `context`: Additional context to enrich the memory
- **Returns**: The unique ID of the stored memory

##### `async search_similar_issues(query: str, limit: int = 5) -> List[Dict[str, Any]]`
- **Description**: Searches for similar past issues and solutions
- **Parameters**:
  - `query`: The current problem or question to match against
  - `limit`: Maximum number of similar memories to return
- **Returns**: List of relevant past memories with their metadata

##### `async get_relevant_context(user_query: str) -> str`
- **Description**: Retrieves relevant context for RAG enhancement
- **Parameters**: `user_query` - The current user query
- **Returns**: Formatted string of relevant past solutions and context

##### `async add_solution_feedback(memory_id: str, feedback: str, rating: int) -> None`
- **Description**: Adds user feedback to a specific memory
- **Parameters**:
  - `memory_id`: The ID of the memory to add feedback to
  - `feedback`: The user's textual feedback
  - `rating`: A numerical rating from 1 to 5

### FileIngestor

The `FileIngestor` class handles file uploads and processing for RAG.

#### Key Methods

##### `async save_uploaded_file(file_name: str, file_content) -> Path`
- **Description**: Saves an uploaded file to the RAG directory
- **Parameters**:
  - `file_name`: The original filename
  - `file_content`: A file-like object containing the content
- **Returns**: Path to the saved file
- **Raises**: `FileProcessingError` if the file cannot be saved

##### `async ingest_file(file_path: Path) -> bool`
- **Description**: Ingests a single file into the knowledge graph
- **Parameters**: `file_path` - Path to the file to ingest
- **Returns**: True if ingestion was successful, False otherwise

### OptimizedTWSClient

The `OptimizedTWSClient` class provides optimized access to TWS APIs.

#### Key Methods

##### `async check_connection() -> bool`
- **Description**: Verifies the connection to the TWS server
- **Returns**: True if connection is active, False otherwise

##### `async get_workstations_status() -> List[WorkstationStatus]`
- **Description**: Retrieves the status of all workstations
- **Returns**: List of workstation status objects
- **Features**: Caching enabled for performance

##### `async get_jobs_status() -> List[JobStatus]`
- **Description**: Retrieves the status of all jobs
- **Returns**: List of job status objects
- **Features**: Caching enabled for performance

##### `async get_critical_path_status() -> List[CriticalJob]`
- **Description**: Retrieves the status of jobs in the critical path
- **Returns**: List of critical job objects
- **Features**: Caching enabled for performance

##### `async get_system_status() -> SystemStatus`
- **Description**: Retrieves comprehensive system status
- **Returns**: Complete system status object

### ConnectionManager

The `ConnectionManager` class manages WebSocket connections.

#### Key Methods

##### `async connect(websocket: WebSocket) -> None`
- **Description**: Accepts a new WebSocket connection
- **Parameters**: `websocket` - The WebSocket connection to accept

##### `async disconnect(websocket: WebSocket) -> None`
- **Description**: Removes a WebSocket connection
- **Parameters**: `websocket` - The WebSocket connection to remove

##### `async broadcast(message: str) -> None`
- **Description**: Sends a message to all connected clients
- **Parameters**: `message` - The message to broadcast

##### `async broadcast_json(data: Dict[str, Any]) -> None`
- **Description**: Sends JSON data to all connected clients
- **Parameters**: `data` - The JSON data to broadcast

## Data Models

### AgentConfig

Represents the configuration for a single AI agent.

```python
class AgentConfig(BaseModel):
    id: str
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str]
    model_name: str = "llama3:latest"
    memory: bool = True
    verbose: bool = False
```

### SystemStatus

Represents the overall status of the TWS environment.

```python
class SystemStatus(BaseModel):
    workstations: List[WorkstationStatus]
    jobs: List[JobStatus]
    critical_jobs: List[CriticalJob]
```

### WorkstationStatus

Represents the status of a single TWS workstation.

```python
class WorkstationStatus(BaseModel):
    name: str
    status: str  # e.g., 'LINKED', 'DOWN'
    type: str   # e.g., 'FTA', 'MASTER'
```

### JobStatus

Represents the status of a single TWS job.

```python
class JobStatus(BaseModel):
    name: str
    workstation: str
    status: str  # e.g., 'SUCC', 'ABEND'
    job_stream: str
```

### CriticalJob

Represents a job that is part of the critical path.

```python
class CriticalJob(BaseModel):
    job_id: int
    job_name: str
    status: str
    start_time: str
```

### ReviewAction

Represents a human review action for flagged memories.

```python
class ReviewAction(BaseModel):
    memory_id: str
    action: str  # "approve" or "reject"
```

### ReviewRequest

Represents a review request for input validation testing.

```python
class ReviewRequest(BaseModel):
    content: str = Field(..., max_length=1000)
```

### ExecuteRequest

Represents an execute request for command validation testing.

```python
class ExecuteRequest(BaseModel):
    command: str
```

## Services

### TWS Tools

#### TWSStatusTool

A tool for retrieving the overall status of the TWS environment.

##### `async get_tws_status() -> str`
- **Description**: Fetches the current status of TWS workstations and jobs
- **Returns**: A string summarizing the status of workstations and jobs
- **Error Handling**: Comprehensive error handling for connection, timeout, and network errors

#### TWSTroubleshootingTool

A tool for diagnosing and providing solutions for TWS issues.

##### `async analyze_failures() -> str`
- **Description**: Analyzes failed jobs and down workstations to identify root causes
- **Returns**: A string with diagnostic analysis of TWS failures
- **Features**: Identifies jobs in 'ABEND' state and workstations in 'DOWN' state

### AsyncTTLCache

A truly asynchronous TTL cache for optimal performance.

#### Key Methods

##### `async get(key: str) -> Any | None`
- **Description**: Asynchronously retrieve an item from the cache
- **Parameters**: `key` - Cache key to retrieve
- **Returns**: Cached value if exists and not expired, None otherwise

##### `async set(key: str, value: Any, ttl_seconds: Optional[int] = None) -> None`
- **Description**: Asynchronously add an item to the cache
- **Parameters**:
  - `key` - Cache key
  - `value` - Value to cache
  - `ttl_seconds` - Optional TTL override for this specific entry

##### `async delete(key: str) -> bool`
- **Description**: Asynchronously delete an item from the cache
- **Parameters**: `key` - Cache key to delete
- **Returns**: True if item was deleted, False if not found

## Usage Examples

### Basic Chat Integration

```python
import asyncio
import websockets
import json

async def chat_with_agent(agent_id: str, message: str):
    uri = f"ws://localhost:8000/ws/{agent_id}"
    
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(message)
        
        # Receive response
        async for response in websocket:
            data = json.loads(response)
            print(f"{data['sender']}: {data['message']}")
            
            if data.get('is_final'):
                break

# Usage
asyncio.run(chat_with_agent("tws-specialist", "What's the status of the TWS system?"))
```

### File Upload for RAG

```python
import httpx

async def upload_document(file_path: str):
    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = await client.post(
                "http://localhost:8000/api/rag/upload",
                files=files
            )
            return response.json()

# Usage
result = await upload_document("document.pdf")
print(f"Uploaded: {result['filename']}")
```

### TWS Status Monitoring

```python
import httpx

async def get_tws_status():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/status")
        return response.json()

# Usage
status = await get_tws_status()
print(f"Workstations: {len(status['workstations'])}")
print(f"Jobs: {len(status['jobs'])}")
```

### Agent Management

```python
import httpx

async def get_agents():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/agents")
        return response.json()

# Usage
agents = await get_agents()
for agent in agents:
    print(f"Agent: {agent['name']} - {agent['role']}")
```

## Integration Guide

### 1. Setting Up the Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TWS_HOST=your-tws-host
export TWS_PORT=your-tws-port
export TWS_USER=your-username
export TWS_PASSWORD=your-password
```

### 2. Configuration

Create an agent configuration file (`agents.json`):

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

### 3. Starting the Application

```bash
# Development mode
uvicorn resync.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn resync.main:app --host 0.0.0.0 --port 8000
```

### 4. WebSocket Client Integration

```javascript
// Frontend WebSocket integration
class ResyncChat {
    constructor(agentId) {
        this.agentId = agentId;
        this.ws = null;
    }
    
    connect() {
        this.ws = new WebSocket(`ws://localhost:8000/ws/${this.agentId}`);
        
        this.ws.onopen = () => {
            console.log('Connected to agent');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('Disconnected from agent');
        };
    }
    
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        }
    }
    
    handleMessage(data) {
        // Handle different message types
        switch(data.type) {
            case 'message':
                this.displayMessage(data.sender, data.message);
                break;
            case 'stream':
                this.appendToStream(data.message);
                break;
            case 'error':
                this.displayError(data.message);
                break;
        }
    }
}

// Usage
const chat = new ResyncChat('tws-specialist');
chat.connect();
```

### 5. Error Handling

The system provides comprehensive error handling:

- **Connection Errors**: Automatic retry with exponential backoff
- **Timeout Errors**: Configurable timeouts for all operations
- **Validation Errors**: Input validation with detailed error messages
- **Security Errors**: XSS and injection attack prevention

### 6. Monitoring and Metrics

Access application metrics at `/api/metrics` in Prometheus format:

```bash
curl http://localhost:8000/api/metrics
```

### 7. Health Checks

Monitor application health:

```bash
# Application health
curl http://localhost:8000/api/health/app

# TWS connection health
curl http://localhost:8000/api/health/tws
```

This comprehensive documentation covers all public APIs, functions, and components of the Resync system, providing developers with the information needed to integrate and extend the system effectively.