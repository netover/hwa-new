# Makefile for the Resync Project
# Provides a set of commands to manage the application lifecycle.

# --- Variables ---
# Use the project's virtual environment's Python interpreter
PYTHON = .venv/bin/python
PIP = .venv/bin/pip
AGNO = .venv/bin/agno
# Define the source directory for formatting and linting
SRC_DIR = resync tests

# --- Environment Setup ---
.PHONY: venv
venv:
	@echo "--- Creating virtual environment in .venv ---"
	python3 -m venv .venv
	@echo "--- Virtual environment created. Activate with 'source .venv/bin/activate' ---"

.PHONY: install
install: venv
	@echo "--- Installing dependencies from requirements.txt ---"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "--- Installing testing dependencies ---"
	$(PIP) install pytest pytest-asyncio pytest-playwright
	@echo "--- Installing Playwright browsers ---"
	.venv/bin/playwright install --with-deps
	@echo "--- Installation complete ---"

# --- Code Quality & Formatting ---
.PHONY: format
format:
	@echo "--- Formatting code with Black and Ruff ---"
	$(PYTHON) -m black $(SRC_DIR)
	$(PYTHON) -m ruff format $(SRC_DIR)

.PHONY: lint
lint:
	@echo "--- Linting with Ruff ---"
	$(PYTHON) -m ruff check $(SRC_DIR)
	@echo "--- Type-checking with MyPy ---"
	$(PYTHON) -m mypy $(SRC_DIR)

.PHONY: check
check: format lint

# --- Application Lifecycle ---
.PHONY: run
run:
	@echo "--- Starting Resync application with Uvicorn ---"
	.venv/bin/uvicorn resync.main:app --reload

.PHONY: run-llm
run-llm:
	@echo "--- Starting local LLM server ---"
	$(AGNO) llm --model-path $(LLM_MODEL_PATH)

# --- Configuration Management ---
.PHONY: env
env:
	@echo "--- Generating .env.example from settings ---"
	$(AGNO) settings resync.settings:settings > .env.example
	@echo ".env.example file has been generated. Please review and create a .env file."

# --- Testing ---
.PHONY: test
test:
	@echo "--- Running pytest test suite ---"
	$(PYTHON) -m pytest

# --- Housekeeping ---
.PHONY: clean
clean:
	@echo "--- Cleaning up project ---"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache

.PHONY: help
help:
	@echo "--- Resync Project Makefile ---"
	@echo "Available commands:"
	@echo "  venv          - Create a Python virtual environment."
	@echo "  install       - Install all project dependencies."
	@echo "  format        - Format code using Black and Ruff."
	@echo "  lint          - Lint code with Ruff and type-check with MyPy."
	@echo "  check         - Run both format and lint."
	@echo "  run           - Start the FastAPI application."
	@echo "  run-llm       - Start the local LLM server."
	@echo "  env           - Generate the .env.example file."
	@echo "  test          - Run the pytest test suite."
	@echo "  clean         - Remove temporary files and the virtual environment."
	@echo "--------------------------------"
