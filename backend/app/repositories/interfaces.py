"""Abstract repository interfaces for UTM tracking.

SOLID-O: Open for extension via new concrete implementations.
SOLID-I: Two segregated interfaces — one per aggregate root.
SOLID-D: Services depend on these abstractions, not concrete classes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.utm import ClickEvent, UTMLink


class IUTMLinkRepository(ABC):
    """Interface for UTM link persistence operations."""

    @abstractmethod
    async def create(self, session: AsyncSession, link: UTMLink) -> UTMLink:
        """Persist a new UTM link."""
        ...

    @abstractmethod
    async def get_by_id(self, session: AsyncSession, link_id: UUID) -> Optional[UTMLink]:
        """Retrieve a UTM link by its primary key."""
        ...

    @abstractmethod
    async def get_by_short_code(self, session: AsyncSession, short_code: str) -> Optional[UTMLink]:
        """Retrieve a UTM link by its short code."""
        ...

    @abstractmethod
    async def list_by_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        offset: int,
        limit: int,
    ) -> tuple[list[UTMLink], int]:
        """Return paginated links for a user and the total count."""
        ...

    @abstractmethod
    async def delete(self, session: AsyncSession, link: UTMLink) -> None:
        """Delete a UTM link."""
        ...

    @abstractmethod
    async def short_code_exists(self, session: AsyncSession, short_code: str) -> bool:
        """Check whether a short code is already taken."""
        ...


class IClickEventRepository(ABC):
    """Interface for click event persistence and analytics queries."""

    @abstractmethod
    async def create(self, session: AsyncSession, event: ClickEvent) -> ClickEvent:
        """Persist a new click event."""
        ...

    @abstractmethod
    async def count_by_link(self, session: AsyncSession, utm_link_id: UUID) -> int:
        """Return the total click count for a single UTM link."""
        ...

    @abstractmethod
    async def get_clicks_over_time(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        """Return daily click counts for the last N days for a user's links."""
        ...

    @abstractmethod
    async def get_clicks_by_source(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        """Return click counts grouped by utm_source."""
        ...

    @abstractmethod
    async def get_clicks_by_medium(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        """Return click counts grouped by utm_medium."""
        ...

    @abstractmethod
    async def get_clicks_by_device(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        """Return click counts grouped by device_type."""
        ...

    @abstractmethod
    async def get_clicks_by_browser(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> list[dict]:
        """Return click counts grouped by browser."""
        ...

    @abstractmethod
    async def count_unique_visitors(
        self, session: AsyncSession, user_id: UUID, days: int
    ) -> int:
        """Return count of distinct IP addresses across all user's links."""
        ...
