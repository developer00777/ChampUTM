"""UTM link management API endpoints.

SOLID-S: Router only handles HTTP concerns, delegates all logic to utm_service.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_auth, TokenData
from app.db.postgres import get_db_session
from app.schemas.utm import (
    AnalyticsResponse,
    UTMLinkCreate,
    UTMLinkListResponse,
    UTMLinkResponse,
)
from app.services.utm_service import utm_service

router = APIRouter(prefix="/utm", tags=["UTM Links"])


@router.post("/links", response_model=UTMLinkResponse, status_code=201)
async def create_utm_link(
    data: UTMLinkCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: TokenData = Depends(require_auth),
) -> UTMLinkResponse:
    """Create a new UTM-tagged link."""
    return await utm_service.create_link(session, UUID(current_user.user_id), data)


@router.get("/links", response_model=UTMLinkListResponse)
async def list_utm_links(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
    current_user: TokenData = Depends(require_auth),
) -> UTMLinkListResponse:
    """List all UTM links for the current user."""
    return await utm_service.list_links(session, UUID(current_user.user_id), offset, limit)


@router.get("/links/{link_id}", response_model=UTMLinkResponse)
async def get_utm_link(
    link_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: TokenData = Depends(require_auth),
) -> UTMLinkResponse:
    """Get a single UTM link (must be owned by current user)."""
    return await utm_service.get_link(session, UUID(current_user.user_id), link_id)


@router.delete("/links/{link_id}", status_code=204)
async def delete_utm_link(
    link_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: TokenData = Depends(require_auth),
) -> None:
    """Delete a UTM link (must be owned by current user)."""
    await utm_service.delete_link(session, UUID(current_user.user_id), link_id)


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db_session),
    current_user: TokenData = Depends(require_auth),
) -> AnalyticsResponse:
    """Get aggregated analytics for the current user's links."""
    return await utm_service.get_analytics(session, UUID(current_user.user_id), days)
