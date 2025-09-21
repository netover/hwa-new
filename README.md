# Resync - AI-Powered TWS Dashboard

Resync is a real-time monitoring and management dashboard for HCL Workload Automation (HWA/TWS), powered by a multi-agent AI system using the AGNO framework.

## Features
- Real-time dashboard updated via WebSockets.
- AI-powered chat to query system status.
- Hot-reloading of AI agent configuration.
- Modular and extensible architecture.

## Quick Start

### 1. Prerequisites
- Python 3.12+
- Access to an HCL Workload Automation environment (or run in mock mode).

### 2. Installation
Clone the repository:
```bash
git clone https://github.com/netover/hwa-new.git
cd hwa-new
```

Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file for your environment variables. You can generate a template by running:
```bash
make env
```
This will create a `.env.example` file. Rename it to `.env` and fill in the required values, such as your TWS credentials and the path to your local AI model.

### 4. Running the Application
Start the backend server:
```bash
make run
```
The application will be available at `http://localhost:8000`.

### 5. Running Tests
To run the unit tests and static analysis:
```bash
# Run unit tests
make test

# Run linters and type checker
make fmt
```
