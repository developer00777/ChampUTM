"""API v1 routers."""

from app.api.v1 import auth, health
from app.api.v1.utm import router as utm_router
from app.api.v1.tracking import router as tracking_router

__all__ = ["auth", "health", "utm_router", "tracking_router"]
