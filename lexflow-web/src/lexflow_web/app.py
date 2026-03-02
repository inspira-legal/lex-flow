"""FastAPI application for LexFlow web frontend."""

import argparse
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from lexflow_web.api import router as api_router
from lexflow_web.websocket import router as ws_router
from lexflow_web.triggers import build_trigger_router

logger = logging.getLogger(__name__)


def create_app(workflow_paths: list[str] | None = None) -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="LexFlow Web",
        description="Web frontend for LexFlow workflow visualization and execution",
        version="0.1.0",
    )

    app.include_router(api_router, prefix="/api")
    app.include_router(ws_router)

    if workflow_paths is None:
        env_val = os.environ.get("LEXFLOW_TRIGGER_WORKFLOWS", "")
        if env_val:
            workflow_paths = [p.strip() for p in env_val.split(",") if p.strip()]

    if workflow_paths:
        trigger_router = build_trigger_router(workflow_paths)
        app.include_router(trigger_router)
        logger.info(
            "Registered trigger routes from %d workflow(s)", len(workflow_paths)
        )

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
    parser.add_argument(
        "-w",
        "--workflow",
        action="append",
        default=[],
        help="Workflow file with HTTP triggers (repeatable)",
    )
    args = parser.parse_args()

    if args.workflow:
        os.environ["LEXFLOW_TRIGGER_WORKFLOWS"] = ",".join(args.workflow)

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
