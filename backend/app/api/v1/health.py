"""Health check endpoint."""

from fastapi import APIRouter, Response
from sqlalchemy import text
from app.db.postgres import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(response: Response):
    """Basic health check with database connectivity test."""
    try:
        async with get_db() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        response.status_code = 503
        return {"status": "unhealthy", "database": f"error: {str(e)}"}
