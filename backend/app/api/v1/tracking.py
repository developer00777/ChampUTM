"""Public redirect endpoint for short URLs.

SOLID-S: Separate router for public redirect — no auth, different security model.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db_session
from app.services.utm_service import utm_service

router = APIRouter(prefix="/r", tags=["Tracking"])


@router.get("/{short_code}")
async def redirect_short_link(
    short_code: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    """Resolve a short code, record a click, and redirect to the destination URL."""
    destination_url = await utm_service.record_click(session, short_code, request)
    if destination_url is None:
        raise HTTPException(status_code=404, detail="Short link not found")
    return RedirectResponse(url=destination_url, status_code=302)
