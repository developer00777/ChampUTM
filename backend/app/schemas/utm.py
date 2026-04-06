"""Pydantic schemas for UTM links and analytics.

SOLID-S: Schemas are separate from ORM models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class UTMLinkCreate(BaseModel):
    title: Optional[str] = None
    destination_url: str
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None


class UTMLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: Optional[str]
    destination_url: str
    short_code: str
    utm_source: Optional[str]
    utm_medium: Optional[str]
    utm_campaign: Optional[str]
    utm_term: Optional[str]
    utm_content: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Computed fields (populated by the service layer)
    full_url: str = ""
    redirect_url: str = ""
    click_count: int = 0


class UTMLinkListResponse(BaseModel):
    items: list[UTMLinkResponse]
    total: int
    offset: int
    limit: int


# ── Analytics ──────────────────────────────────────────────────────────────


class ClicksOverTime(BaseModel):
    date: str
    count: int


class ClicksByDimension(BaseModel):
    label: str
    count: int


class AnalyticsResponse(BaseModel):
    clicks_over_time: list[ClicksOverTime]
    clicks_by_source: list[ClicksByDimension]
    clicks_by_medium: list[ClicksByDimension]
    clicks_by_device: list[ClicksByDimension]
    clicks_by_browser: list[ClicksByDimension]
    clicks_by_country: list[ClicksByDimension]
    total_clicks: int
    unique_visitors: int
    total_links: int
    vpn_clicks: int
    days: int


class LinkAnalyticsResponse(BaseModel):
    link: UTMLinkResponse
    clicks_over_time: list[ClicksOverTime]
    clicks_by_device: list[ClicksByDimension]
    clicks_by_browser: list[ClicksByDimension]
    clicks_by_country: list[ClicksByDimension]
    total_clicks: int
    unique_visitors: int
    vpn_clicks: int
    days: int


class VpnFlagsResponse(BaseModel):
    vpn_clicks: int
    by_country: list[ClicksByDimension]   # VPN clicks grouped by exit-node country
    by_isp: list[ClicksByDimension]       # VPN clicks grouped by ISP/org (provider name)
    days: int
