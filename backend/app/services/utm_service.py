"""UTM link business logic.

SOLID-D: Receives IUTMLinkRepository + IClickEventRepository via __init__,
         never imports concrete classes directly.
"""

from __future__ import annotations

import logging
import secrets
import string
from typing import Optional
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
from uuid import UUID

import httpx
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.models.utm import ClickEvent, UTMLink
from app.repositories.interfaces import IClickEventRepository, IUTMLinkRepository
from app.repositories.utm_repository import (
    PostgresClickEventRepository,
    PostgresUTMLinkRepository,
)
from app.core.config import settings
from app.schemas.utm import (
    AnalyticsResponse,
    ClicksByDimension,
    ClicksOverTime,
    LinkAnalyticsResponse,
    UTMLinkCreate,
    UTMLinkListResponse,
    UTMLinkResponse,
)


# ── Private helpers ────────────────────────────────────────────────────────

_ALPHABET = string.ascii_letters + string.digits


def _generate_short_code() -> str:
    """Generate an 8-character alphanumeric short code."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(8))


def _build_full_url(destination_url: str, link: UTMLink) -> str:
    """Merge UTM parameters into destination_url, preserving any existing QS."""
    parsed = urlparse(destination_url)
    existing_qs = parse_qs(parsed.query, keep_blank_values=True)

    utm_params = {
        k: v
        for k, v in {
            "utm_source": link.utm_source,
            "utm_medium": link.utm_medium,
            "utm_campaign": link.utm_campaign,
            "utm_term": link.utm_term,
            "utm_content": link.utm_content,
        }.items()
        if v
    }

    # UTM params override existing ones
    merged = {k: [v] for k, v in {**{k: v[0] for k, v in existing_qs.items()}, **utm_params}.items()}
    new_query = urlencode({k: v[0] for k, v in merged.items()})

    return urlunparse(parsed._replace(query=new_query))


def _detect_device_type(user_agent: str) -> str:
    """Classify device type from User-Agent string."""
    ua = user_agent.lower()
    if any(bot in ua for bot in ("bot", "crawler", "spider", "slurp", "googlebot")):
        return "bot"
    if any(m in ua for m in ("mobile", "android", "iphone", "ipod", "blackberry", "windows phone")):
        return "mobile"
    if any(t in ua for t in ("tablet", "ipad")):
        return "tablet"
    return "desktop"


def _detect_browser(user_agent: str) -> str:
    """Classify browser from User-Agent string."""
    ua = user_agent.lower()
    if "edg/" in ua or "edge/" in ua:
        return "Edge"
    if "chrome/" in ua and "chromium" not in ua:
        return "Chrome"
    if "firefox/" in ua:
        return "Firefox"
    if "safari/" in ua and "chrome" not in ua:
        return "Safari"
    if "opera/" in ua or "opr/" in ua:
        return "Opera"
    return "Other"


def _get_client_ip(request: Request) -> str:
    """Extract real client IP, respecting X-Forwarded-For."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ── GeoIP + VPN helpers ────────────────────────────────────────────────────

_PRIVATE_IPS = ("unknown", "127.0.0.1", "::1", "localhost")


async def _lookup_ip_info(ip: str) -> dict | None:
    """
    Single ip-api.com call returning country, region, city, and VPN/proxy flag.
    Returns None on private IPs, errors, or timeouts — always best-effort.
    Fields: countryCode, regionName, city, proxy (bool)
    Free tier limit: 45 req/min. Silent fail on any error.
    """
    if not ip or ip in _PRIVATE_IPS or ip.startswith("192.168.") or ip.startswith("10."):
        return None
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(
                f"http://ip-api.com/json/{ip}",
                params={"fields": "status,countryCode,regionName,city,proxy"},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    return {
                        "country": data.get("countryCode"),   # e.g. "US"
                        "region": data.get("regionName"),     # e.g. "California"
                        "city": data.get("city"),             # e.g. "San Francisco"
                        "is_vpn": bool(data.get("proxy", False)),
                    }
    except Exception:
        pass
    return None


# ── Service ────────────────────────────────────────────────────────────────


class UTMService:
    """
    Orchestrates UTM link and analytics operations.

    SOLID-D: depends on repository interfaces injected at construction time.
    """

    def __init__(
        self,
        link_repo: IUTMLinkRepository,
        click_repo: IClickEventRepository,
    ) -> None:
        self._link_repo = link_repo
        self._click_repo = click_repo

    # ── Helpers ────────────────────────────────────────────────────────────

    def _to_response(self, link: UTMLink, click_count: int = 0) -> UTMLinkResponse:
        full_url = _build_full_url(link.destination_url, link)
        redirect_url = f"/r/{link.short_code}"
        resp = UTMLinkResponse.model_validate(link)
        resp.full_url = full_url
        resp.redirect_url = redirect_url
        resp.click_count = click_count
        return resp

    # ── Link CRUD ──────────────────────────────────────────────────────────

    async def create_link(
        self, session: AsyncSession, user_id: UUID, data: UTMLinkCreate
    ) -> UTMLinkResponse:
        # Generate a unique short code (max 5 retries)
        for _ in range(5):
            short_code = _generate_short_code()
            if not await self._link_repo.short_code_exists(session, short_code):
                break
        else:
            raise RuntimeError("Failed to generate a unique short code after 5 attempts")

        link = UTMLink(
            user_id=user_id,
            title=data.title,
            destination_url=data.destination_url,
            short_code=short_code,
            utm_source=data.utm_source,
            utm_medium=data.utm_medium,
            utm_campaign=data.utm_campaign,
            utm_term=data.utm_term,
            utm_content=data.utm_content,
        )
        link = await self._link_repo.create(session, link)
        return self._to_response(link, click_count=0)

    async def list_links(
        self, session: AsyncSession, user_id: UUID, offset: int, limit: int
    ) -> UTMLinkListResponse:
        links, total = await self._link_repo.list_by_user(session, user_id, offset, limit)
        items = []
        for link in links:
            count = await self._click_repo.count_by_link(session, link.id)
            items.append(self._to_response(link, count))
        return UTMLinkListResponse(items=items, total=total, offset=offset, limit=limit)

    async def get_link(
        self, session: AsyncSession, user_id: UUID, link_id: UUID
    ) -> UTMLinkResponse:
        from fastapi import HTTPException

        link = await self._link_repo.get_by_id(session, link_id)
        if not link or link.user_id != user_id:
            raise HTTPException(status_code=404, detail="UTM link not found")
        count = await self._click_repo.count_by_link(session, link.id)
        return self._to_response(link, count)

    async def delete_link(
        self, session: AsyncSession, user_id: UUID, link_id: UUID
    ) -> None:
        from fastapi import HTTPException

        link = await self._link_repo.get_by_id(session, link_id)
        if not link or link.user_id != user_id:
            raise HTTPException(status_code=404, detail="UTM link not found")
        await self._link_repo.delete(session, link)

    # ── Click tracking ─────────────────────────────────────────────────────

    async def record_click(
        self, session: AsyncSession, short_code: str, request: Request
    ) -> Optional[str]:
        """Return destination URL for redirect (None if short_code not found)."""
        link = await self._link_repo.get_by_short_code(session, short_code)
        if not link:
            return None

        ua = request.headers.get("user-agent", "")
        referrer = request.headers.get("referer", None)
        ip = _get_client_ip(request)

        ip_info = await _lookup_ip_info(ip) if settings.vpn_detection_enabled else None

        event = ClickEvent(
            utm_link_id=link.id,
            ip_address=ip,
            user_agent=ua or None,
            referrer=referrer,
            device_type=_detect_device_type(ua) if ua else "unknown",
            browser=_detect_browser(ua) if ua else "unknown",
            country=ip_info["country"] if ip_info else None,
            region=ip_info["region"] if ip_info else None,
            city=ip_info["city"] if ip_info else None,
            is_vpn=ip_info["is_vpn"] if ip_info else False,
        )
        await self._click_repo.create(session, event)
        # Return the full UTM-tagged URL so the redirect carries all params
        return _build_full_url(link.destination_url, link)

    # ── Analytics ──────────────────────────────────────────────────────────

    async def get_analytics(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> AnalyticsResponse:
        from sqlalchemy import func, select
        from app.models.utm import ClickEvent as CE, UTMLink as UL

        # Total links
        total_links_result = await session.execute(
            select(func.count()).select_from(UL).where(UL.user_id == user_id)
        )
        total_links = total_links_result.scalar_one()

        clicks_over_time_raw = await self._click_repo.get_clicks_over_time(session, user_id, days)
        clicks_by_source_raw = await self._click_repo.get_clicks_by_source(session, user_id, days)
        clicks_by_medium_raw = await self._click_repo.get_clicks_by_medium(session, user_id, days)
        clicks_by_device_raw = await self._click_repo.get_clicks_by_device(session, user_id, days)
        clicks_by_browser_raw = await self._click_repo.get_clicks_by_browser(session, user_id, days)
        clicks_by_country_raw = await self._click_repo.get_clicks_by_country(session, user_id, days)
        unique_visitors = await self._click_repo.count_unique_visitors(session, user_id, days)
        vpn_clicks = await self._click_repo.count_vpn_clicks(session, user_id, days)

        total_clicks = sum(r["count"] for r in clicks_over_time_raw)

        return AnalyticsResponse(
            clicks_over_time=[ClicksOverTime(**r) for r in clicks_over_time_raw],
            clicks_by_source=[
                ClicksByDimension(label=r["source"], count=r["count"])
                for r in clicks_by_source_raw
            ],
            clicks_by_medium=[
                ClicksByDimension(label=r["medium"], count=r["count"])
                for r in clicks_by_medium_raw
            ],
            clicks_by_device=[
                ClicksByDimension(label=r["device"], count=r["count"])
                for r in clicks_by_device_raw
            ],
            clicks_by_browser=[
                ClicksByDimension(label=r["browser"], count=r["count"])
                for r in clicks_by_browser_raw
            ],
            clicks_by_country=[
                ClicksByDimension(label=r["country"], count=r["count"])
                for r in clicks_by_country_raw
            ],
            total_clicks=total_clicks,
            unique_visitors=unique_visitors,
            total_links=total_links,
            vpn_clicks=vpn_clicks,
            days=days,
        )


    async def get_link_analytics(
        self, session: AsyncSession, user_id: UUID, link_id: UUID, days: int
    ) -> LinkAnalyticsResponse:
        from fastapi import HTTPException

        link = await self._link_repo.get_by_id(session, link_id)
        if not link or link.user_id != user_id:
            raise HTTPException(status_code=404, detail="UTM link not found")

        click_count = await self._click_repo.count_by_link(session, link.id)
        link_response = self._to_response(link, click_count)

        clicks_over_time_raw = await self._click_repo.get_clicks_over_time_for_link(session, link_id, days)
        clicks_by_device_raw = await self._click_repo.get_clicks_by_device_for_link(session, link_id, days)
        clicks_by_browser_raw = await self._click_repo.get_clicks_by_browser_for_link(session, link_id, days)
        clicks_by_country_raw = await self._click_repo.get_clicks_by_country_for_link(session, link_id, days)
        unique_visitors = await self._click_repo.count_unique_visitors_for_link(session, link_id, days)
        vpn_clicks = await self._click_repo.count_vpn_clicks_for_link(session, link_id, days)
        total_clicks = sum(r["count"] for r in clicks_over_time_raw)

        return LinkAnalyticsResponse(
            link=link_response,
            clicks_over_time=[ClicksOverTime(**r) for r in clicks_over_time_raw],
            clicks_by_device=[
                ClicksByDimension(label=r["device"], count=r["count"])
                for r in clicks_by_device_raw
            ],
            clicks_by_browser=[
                ClicksByDimension(label=r["browser"], count=r["count"])
                for r in clicks_by_browser_raw
            ],
            clicks_by_country=[
                ClicksByDimension(label=r["country"], count=r["count"])
                for r in clicks_by_country_raw
            ],
            total_clicks=total_clicks,
            unique_visitors=unique_visitors,
            vpn_clicks=vpn_clicks,
            days=days,
        )


# Module-level singleton matching the existing user_service pattern
utm_service = UTMService(
    link_repo=PostgresUTMLinkRepository(),
    click_repo=PostgresClickEventRepository(),
)
