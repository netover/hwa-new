"""Main application entry point."""

from resync.app_factory import create_app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    from resync.settings import settings
    
    uvicorn.run(
        app,
        host=getattr(settings, 'server_host', '127.0.0.1'),
        port=getattr(settings, 'server_port', 8000),
        log_config=None  # Use our structured logging
    )
