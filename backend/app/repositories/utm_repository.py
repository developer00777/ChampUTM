"""Concrete PostgreSQL repository implementations for UTM tracking.

SOLID-L: Concrete classes fully satisfy the Liskov substitution principle
         for their abstract parents.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import cast, Date, func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.utm import ClickEvent, UTMLink
from app.repositories.interfaces import IClickEventRepository, IUTMLinkRepository


class PostgresUTMLinkRepository(IUTMLinkRepository):
    """PostgreSQL-backed UTM link repository."""

    async def create(self, session: AsyncSession, link: UTMLink) -> UTMLink:
        session.add(link)
        await session.flush()
        await session.refresh(link)
        return link

    async def get_by_id(self, session: AsyncSession, link_id: UUID) -> Optional[UTMLink]:
        result = await session.execute(select(UTMLink).where(UTMLink.id == link_id))
        return result.scalar_one_or_none()

    async def get_by_short_code(self, session: AsyncSession, short_code: str) -> Optional[UTMLink]:
        result = await session.execute(
            select(UTMLink).where(UTMLink.short_code == short_code)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        offset: int,
        limit: int,
    ) -> tuple[list[UTMLink], int]:
        # Total count
        count_result = await session.execute(
            select(func.count()).select_from(UTMLink).where(UTMLink.user_id == user_id)
        )
        total = count_result.scalar_one()

        # Paginated results, newest first
        result = await session.execute(
            select(UTMLink)
            .where(UTMLink.user_id == user_id)
            .order_by(UTMLink.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        links = list(result.scalars().all())
        return links, total

    async def delete(self, session: AsyncSession, link: UTMLink) -> None:
        await session.delete(link)
        await session.flush()

    async def short_code_exists(self, session: AsyncSession, short_code: str) -> bool:
        result = await session.execute(
            select(func.count()).select_from(UTMLink).where(UTMLink.short_code == short_code)
        )
        return result.scalar_one() > 0


class PostgresClickEventRepository(IClickEventRepository):
    """PostgreSQL-backed click event repository."""

    async def create(self, session: AsyncSession, event: ClickEvent) -> ClickEvent:
        session.add(event)
        await session.flush()
        await session.refresh(event)
        return event

    async def count_by_link(self, session: AsyncSession, utm_link_id: UUID) -> int:
        result = await session.execute(
            select(func.count())
            .select_from(ClickEvent)
            .where(ClickEvent.utm_link_id == utm_link_id)
        )
        return result.scalar_one()

    async def get_clicks_over_time(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                cast(ClickEvent.clicked_at, Date).label("date"),
                func.count().label("count"),
            )
            .join(UTMLink, ClickEvent.utm_link_id == UTMLink.id)
            .where(UTMLink.user_id == user_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .group_by(cast(ClickEvent.clicked_at, Date))
            .order_by(cast(ClickEvent.clicked_at, Date))
        )
        return [{"date": str(row.date), "count": row.count} for row in result]

    async def get_clicks_by_source(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                UTMLink.utm_source.label("source"),
                func.count().label("count"),
            )
            .join(ClickEvent, ClickEvent.utm_link_id == UTMLink.id)
            .where(UTMLink.user_id == user_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .group_by(UTMLink.utm_source)
            .order_by(func.count().desc())
        )
        return [{"source": row.source or "unknown", "count": row.count} for row in result]

    async def get_clicks_by_medium(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                UTMLink.utm_medium.label("medium"),
                func.count().label("count"),
            )
            .join(ClickEvent, ClickEvent.utm_link_id == UTMLink.id)
            .where(UTMLink.user_id == user_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .group_by(UTMLink.utm_medium)
            .order_by(func.count().desc())
        )
        return [{"medium": row.medium or "unknown", "count": row.count} for row in result]

    async def get_clicks_by_device(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                ClickEvent.device_type.label("device"),
                func.count().label("count"),
            )
            .join(UTMLink, ClickEvent.utm_link_id == UTMLink.id)
            .where(UTMLink.user_id == user_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .group_by(ClickEvent.device_type)
            .order_by(func.count().desc())
        )
        return [{"device": row.device or "unknown", "count": row.count} for row in result]

    async def get_clicks_by_browser(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                ClickEvent.browser.label("browser"),
                func.count().label("count"),
            )
            .join(UTMLink, ClickEvent.utm_link_id == UTMLink.id)
            .where(UTMLink.user_id == user_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .group_by(ClickEvent.browser)
            .order_by(func.count().desc())
        )
        return [{"browser": row.browser or "unknown", "count": row.count} for row in result]

    async def count_unique_visitors(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(func.count(func.distinct(ClickEvent.ip_address)))
            .join(UTMLink, ClickEvent.utm_link_id == UTMLink.id)
            .where(UTMLink.user_id == user_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .where(ClickEvent.ip_address.isnot(None))
        )
        return result.scalar_one()

    async def get_clicks_over_time_for_link(
        self, session: AsyncSession, link_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                cast(ClickEvent.clicked_at, Date).label("date"),
                func.count().label("count"),
            )
            .where(ClickEvent.utm_link_id == link_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .group_by(cast(ClickEvent.clicked_at, Date))
            .order_by(cast(ClickEvent.clicked_at, Date))
        )
        return [{"date": str(row.date), "count": row.count} for row in result]

    async def get_clicks_by_device_for_link(
        self, session: AsyncSession, link_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                ClickEvent.device_type.label("device"),
                func.count().label("count"),
            )
            .where(ClickEvent.utm_link_id == link_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .group_by(ClickEvent.device_type)
            .order_by(func.count().desc())
        )
        return [{"device": row.device or "unknown", "count": row.count} for row in result]

    async def get_clicks_by_browser_for_link(
        self, session: AsyncSession, link_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                ClickEvent.browser.label("browser"),
                func.count().label("count"),
            )
            .where(ClickEvent.utm_link_id == link_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .group_by(ClickEvent.browser)
            .order_by(func.count().desc())
        )
        return [{"browser": row.browser or "unknown", "count": row.count} for row in result]

    async def count_unique_visitors_for_link(
        self, session: AsyncSession, link_id: UUID, days: int
    ) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(func.count(func.distinct(ClickEvent.ip_address)))
            .where(ClickEvent.utm_link_id == link_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .where(ClickEvent.ip_address.isnot(None))
        )
        return result.scalar_one()

    async def get_clicks_by_country(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                ClickEvent.country.label("country"),
                func.count().label("count"),
            )
            .join(UTMLink, ClickEvent.utm_link_id == UTMLink.id)
            .where(UTMLink.user_id == user_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .where(ClickEvent.country.isnot(None))
            .group_by(ClickEvent.country)
            .order_by(func.count().desc())
        )
        return [{"country": row.country, "count": row.count} for row in result]

    async def get_clicks_by_country_for_link(
        self, session: AsyncSession, link_id: UUID, days: int
    ) -> list[dict]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(
                ClickEvent.country.label("country"),
                func.count().label("count"),
            )
            .where(ClickEvent.utm_link_id == link_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .where(ClickEvent.country.isnot(None))
            .group_by(ClickEvent.country)
            .order_by(func.count().desc())
        )
        return [{"country": row.country, "count": row.count} for row in result]

    async def count_vpn_clicks(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(func.count())
            .select_from(ClickEvent)
            .join(UTMLink, ClickEvent.utm_link_id == UTMLink.id)
            .where(UTMLink.user_id == user_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .where(ClickEvent.is_vpn.is_(True))
        )
        return result.scalar_one()

    async def count_vpn_clicks_for_link(
        self, session: AsyncSession, link_id: UUID, days: int
    ) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        result = await session.execute(
            select(func.count())
            .select_from(ClickEvent)
            .where(ClickEvent.utm_link_id == link_id)
            .where(ClickEvent.clicked_at >= cutoff)
            .where(ClickEvent.is_vpn.is_(True))
        )
        return result.scalar_one()
