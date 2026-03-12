"""
User model for PostgreSQL persistence.

Simplified single-user authentication model for ChampUTM.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.db.postgres import Base


class User(Base):
    """User model with authentication."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    role = Column(String(50), default="user")  # user, admin

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Onboarding progress tracking (for interactive tutorials)
    onboarding_progress = Column(JSON, default=lambda: {"completed_tours": [], "skipped_tours": []})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
