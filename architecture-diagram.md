# Resync System Architecture: A Detailed Overview (Post-Hardening)

The Resync application is a sophisticated, AI-powered monitoring and troubleshooting platform for HCL Workload Automation (TWS). It is designed with a modular, asynchronous architecture to deliver real-time, intelligent operational insights and to continuously learn from its interactions. This document details its architecture, data flows, and the recent enhancements made to improve robustness and performance.

## High-Level Architecture Diagram

The architecture is layered, separating concerns from the user interface down to external service integration.

```mermaid
graph TD
    subgraph "User Interface"
        A[User] --> B[Chat UI<br>templates/index.html]
        B --> E
        U[Human Reviewer] --> T[Review UI<br>templates/revisao.html]
        T --> V
    end

    subgraph "API Layer (FastAPI)"
        C[FastAPI App<br>resync/main.py]
        E[WebSocket API<br>resync/api/chat.py]
        V[Audit API<br>resync/api/audit.py]
        C --> E
        C --> V
    end

    subgraph "Core Logic"
        G[AgentManager<br>resync/core/agent_manager.py]
        K[Knowledge Graph<br>resync/core/knowledge_graph.py]
        M[IA Auditor<br>resync/core/ia_auditor.py]
        S[Scheduler (APScheduler)]
        E --> G
        V --> K
        G --> K
        G --> J
        M --> K
        M --> L
        S --> M
    end
    
    subgraph "AI / Data Layer"
        I[Agent Config<br>config/runtime.json]
        J[TWS Tools<br>resync/tool_definitions/tws_tools.py]
        L[LLM Service<br>resync/core/utils/llm.py]
        P[Vector Store<br>Mem0 AI + Qdrant]
        G --> I
        K --> P
    end

    subgraph "External Services"
        H[OptimizedTWSClient<br>resync/services/tws_service.py]
        N[HCL TWS Server]
        J --> H
        H --> N
    end

    %% Styling
    style A fill:#c9f,stroke:#333,stroke-width:2px
    style U fill:#c9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style T fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#9f9,stroke:#333,stroke-width:2px
    style E fill:#aef,stroke:#333,stroke-width:2px
    style V fill:#aef,stroke:#333,stroke-width:2px
    style G fill:#ff6,stroke:#333,stroke-width:2px
    style K fill:#f96,stroke:#333,stroke-width:2px
    style M fill:#f96,stroke:#333,stroke-width:2px
    style S fill:#f96,stroke:#333,stroke-width:2px
    style I fill:#ddf,stroke:#333,stroke-width:2px
    style J fill:#ff6,stroke:#333,stroke-width:2px
    style L fill:#f69,stroke:#333,stroke-width:2px
    style P fill:#f69,stroke:#333,stroke-width:2px
    style H fill:#e96,stroke:#333,stroke-width:2px
    style N fill:#f66,stroke:#333,stroke-width:2px
```

## End-to-End Control and Data Flow

The system's intelligence emerges from a well-orchestrated flow of data and control, particularly the "human-in-the-loop" audit cycle.

1.  **User Interaction**: A user sends a message through the **Chat UI**.
2.  **WebSocket Handling**: The **WebSocket API** (`chat.py`) receives the message.
3.  **Context Retrieval (RAG)**: The `chat.py` endpoint queries the **Knowledge Graph** for past, similar interactions.
4.  **Agent Invocation**: The user's query, now enhanced with context, is passed to the relevant AI agent, managed by the **AgentManager**.
5.  **Tool Execution**: If required, the agent uses its assigned **TWS Tools** to fetch live data from the **HCL TWS Server**.
6.  **Response Generation**: The agent's underlying LLM generates a response, which is streamed back to the user.
7.  **Memory Creation**: The complete interaction is saved as a new memory in the **Knowledge Graph**.
8.  **Automated Audit**: The `chat.py` endpoint triggers the **IA Auditor** as a safe, non-blocking background task.
9.  **Self-Correction & Flagging**: The auditor evaluates the new memory. It deletes it if incorrect or adds a `FLAGGED_BY_IA` observation to it if suspicious. A corresponding entry is made in a JSON log file.
10. **Human-in-the-Loop Review**: A **Human Reviewer** navigates to the **Review UI** (`/revisao`), which fetches the log files via the **Audit API**.
11. **Closing the Loop**: The reviewer's "Approve" or "Reject" action calls the `POST /api/audit/review` endpoint, which updates or deletes the memory. Once all items in a log file are reviewed, the reviewer can archive it via a `DELETE` call, cleaning the queue.

---

## Architectural Enhancements for Robustness

Following a deep code audit, several key enhancements were implemented to elevate the system's resilience, performance, and maintainability.

*   **1. Dependency Management (`requirements.txt`):** The project's dependencies were consolidated into a single `requirements.txt` file, and critical missing libraries (`mem0`, `apscheduler`) were added, ensuring reproducible and stable deployments.

*   **2. Asynchronous Task Resilience (`chat.py`):** The background task for the `IA Auditor` is now invoked via a `run_auditor_safely` wrapper. This prevents silent failures by ensuring any exception within the auditor's execution is caught and logged, guaranteeing the self-healing loop remains active.

*   **3. Non-Blocking I/O (`ia_auditor.py`):** The blocking `mem0.search` call within the auditor is now delegated to a thread pool using `asyncio.run_in_executor`. This is a critical performance fix that prevents the entire server from freezing during database searches, ensuring the UI and APIs remain responsive.

*   **4. Atomic State Management (`ia_auditor.py`):** The auditor's logic was re-architected. Instead of relying solely on external log files for state, it now adds a `FLAGGED_BY_IA` observation directly to a memory in the Knowledge Graph. The auditor now intelligently skips any memory that has been previously flagged or manually approved, eliminating redundant processing and preventing race conditions.

*   **5. Log File Lifecycle Management (`audit.py`, `revisao.js`):** A complete lifecycle for review files has been implemented. The review UI now features an "Archive" button that appears after all items in a file are processed. This action calls a new `DELETE /api/audit/flags/{filename}` endpoint, which securely removes the file, ensuring the review queue stays clean and up-to-date.

*   **6. Centralized Configuration (`knowledge_graph.py`, `settings.py`):** All hardcoded model and provider configurations within the `KnowledgeGraph` have been refactored. The component now sources all its settings from the central `settings.py` file, adhering to the project's design principles and simplifying future maintenance.

*   **7. API Completion (`endpoints.py`, `agent_manager.py`):** The previously missing `/api/agents` endpoint has been fully implemented. The `agent_manager` now properly exposes agent configurations, allowing the UI to dynamically discover and list available agents.

---

## Detailed Component Breakdown

### 1. Application Core (`resync/main.py`)

-   **Role**: The central entry point of the application.
-   **Logic**: Uses FastAPI's `lifespan` manager to control startup/shutdown events, including the `IA Auditor` scheduler (`APScheduler`) and a configuration file watcher. It mounts all API routers and serves the frontend.

### 2. Agent Subsystem

-   **`agent_manager.py`**: A Singleton that orchestrates the agent lifecycle. It loads agent definitions from `config/runtime.json` and now correctly exposes these configurations via the `get_all_agents()` method to the API layer.
-   **`tws_tools.py`**: Defines the concrete, read-only actions agents can perform on the TWS system, ensuring safety and predictability.

### 3. Intelligence & Learning Layer

-   **`knowledge_graph.py`**: A wrapper for **Mem0 AI** that provides a persistent, searchable memory. Its public interface is now cleaner, offering dedicated methods like `get_all_recent_conversations()` for auditing, which prevents direct client access and improves encapsulation. It is now fully configurable via `settings.py`.
-   **`ia_auditor.py`**: The system's self-correction mechanism. Its logic has been significantly hardened: it uses non-blocking I/O for database searches and marks memories with an internal `FLAGGED_BY_IA` status to manage state atomically.

### 4. API & Frontend Layer

-   **`chat.py`**: Implements the primary WebSocket endpoint for user interaction. It now triggers the `IA Auditor` via a safe, exception-handling background task, making the audit process more resilient.
-   **`endpoints.py`**: Exposes the application's REST endpoints. It now includes the crucial `/api/agents` endpoint, allowing UIs to dynamically discover available agents.
-   **`audit.py`**: Provides the backend for the human review process. It now includes a `DELETE` endpoint to allow for the cleanup of processed review files, completing the log lifecycle.
-   **`revisao.html` & `revisao.js`**: An interactive dashboard for the human-in-the-loop process, now with the ability to archive completed review files.

### 5. TWS Integration (`resync/services/tws_service.py`)

-   **`OptimizedTWSClient`**: A robust, asynchronous client for communicating with the HCL TWS API, featuring connection pooling and a TTL cache. The `verify=False` setting remains as per instruction for non-production environments.
