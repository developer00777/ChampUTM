"""UTM link and click event SQLAlchemy models.

SOLID-S: Pure data definitions, zero business logic.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base


class UTMLink(Base):
    __tablename__ = "utm_links"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    destination_url: Mapped[str] = mapped_column(Text, nullable=False)
    short_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)

    utm_source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_medium: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_term: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_content: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    click_events: Mapped[list[ClickEvent]] = relationship(
        "ClickEvent", back_populates="utm_link", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_utm_links_user_created", "user_id", "created_at"),
    )


class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    utm_link_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("utm_links.id", ondelete="CASCADE"), nullable=False
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 safe
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)    # ISO 3166-1 alpha-2
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "California"
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)    # e.g. "San Francisco"
    is_vpn: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # desktop/mobile/tablet/bot
    browser: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    utm_link: Mapped[UTMLink] = relationship("UTMLink", back_populates="click_events")

    __table_args__ = (
        Index("ix_click_events_link_clicked", "utm_link_id", "clicked_at"),
    )
