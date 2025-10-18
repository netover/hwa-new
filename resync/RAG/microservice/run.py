#!/usr/bin/env python3
"""
RAG Microservice Launcher

This script launches the RAG microservice with proper imports.
"""

import sys
import os

# Add the microservice directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Set up package structure
if __name__ == "__main__":
    # Create the app
    from main import app

    import uvicorn
    print("🚀 Starting RAG Microservice...")
    print(f"📁 Working directory: {current_dir}")
    print(f"🐍 Python path: {sys.path[0]}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )