"""Pydantic schemas for request/response validation."""

from app.schemas.utm import (
    AnalyticsResponse,
    ClicksByDimension,
    ClicksOverTime,
    UTMLinkCreate,
    UTMLinkListResponse,
    UTMLinkResponse,
)

__all__ = [
    "UTMLinkCreate",
    "UTMLinkResponse",
    "UTMLinkListResponse",
    "ClicksOverTime",
    "ClicksByDimension",
    "AnalyticsResponse",
]
