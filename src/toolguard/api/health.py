"""Health and metrics endpoints."""

from fastapi import APIRouter

from toolguard.config import app_config

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Return service health status and configured scanner lists.

    Returns:
        JSON with ``status`` and ``scanners`` breakdown per scan type.
    """
    return {
        "status": "healthy",
        "scanners": {
            "input": app_config.scanners.input,
            "output": app_config.scanners.output,
            "tool_call": app_config.scanners.tool_call,
        },
    }


@router.get("/metrics")
async def metrics() -> dict:
    """Return basic service metrics (placeholder for future Prometheus export).

    Returns:
        JSON with scanner counts per scan type.
    """
    return {
        "scanner_counts": {
            "input": len(app_config.scanners.input),
            "output": len(app_config.scanners.output),
            "tool_call": len(app_config.scanners.tool_call),
        }
    }
