"""Liveness (/health) and readiness (/health/ready) probes."""

import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: the process is up. Does not touch external dependencies."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/health/ready")
async def readiness(response: Response, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    """Readiness: verifies the database connection."""
    checks: dict[str, str] = {}
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:  # noqa: BLE001 - report any DB failure as not ready
        logger.exception("Database readiness check failed")
        checks["database"] = "error"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    ready = all(v == "ok" for v in checks.values())
    return {"status": "ok" if ready else "degraded", "checks": checks}
