"""FastAPI application for LexFlow web frontend."""

import argparse
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from lexflow_web.api import router as api_router
from lexflow_web.websocket import router as ws_router
from lexflow_web.workflows import router as workflows_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="LexFlow Web",
        description="Web frontend for LexFlow workflow visualization and execution",
        version="0.1.0",
    )

    # Include routers
    app.include_router(api_router, prefix="/api")
    app.include_router(workflows_router, prefix="/api/workflows")
    app.include_router(ws_router)

    # Static files
    static_dir = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def index():
        """Serve the main page."""
        return FileResponse(static_dir / "index.html")

    return app


def run():
    """Entry point for lexflow-web command."""
    parser = argparse.ArgumentParser(description="LexFlow Web Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    import uvicorn

    uvicorn.run(
        "lexflow_web.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    run()
