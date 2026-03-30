"""ToolGuard FastAPI application entry point."""

from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI

from toolguard.api.health import router as health_router
from toolguard.api.scan import router as scan_router
from toolguard.config import app_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s  %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="ToolGuard",
    description="AI application security layer — hiveden",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(scan_router)
app.include_router(health_router)


@app.get("/")
async def root() -> dict:
    """Service root — returns a brief status message."""
    return {"service": "toolguard", "status": "ok", "version": "0.1.0"}


def start() -> None:
    """Start the uvicorn server (used by the ``toolguard`` CLI entry point)."""
    uvicorn.run(
        "toolguard.main:app",
        host=app_config.server.host,
        port=app_config.server.port,
        log_level=app_config.server.log_level,
        reload=False,
    )


if __name__ == "__main__":
    start()
