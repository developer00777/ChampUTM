"""
ChampUTM - FastAPI Backend

Main application entry point.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.db.postgres import init_db, close_db, get_db
from app.services.user_service import user_service
from app.middleware.rate_limit import setup_rate_limiting

# Import routers
from app.api.v1 import auth, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    import asyncio
    import time

    startup_start = time.time()

    # Startup
    logger.info("=== LIFESPAN START ===")
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Environment: %s", settings.environment)
    logger.info("PostgreSQL: %s:%s", settings.postgres_host, settings.postgres_port)

    # Validate production settings (warn but don't crash — let healthcheck pass)
    try:
        settings.validate_production_settings()
        logger.info("Production settings validated successfully")
    except ValueError as e:
        logger.error("Production settings validation failed: %s", e)
        logger.error("Server starting anyway — fix env vars to resolve")

    # Initialize PostgreSQL with timeout so lifespan doesn't block healthcheck
    try:
        await asyncio.wait_for(init_db(), timeout=15.0)
        logger.info("PostgreSQL connected and tables created (%.1fs)", time.time() - startup_start)

        # Create default admin user (development only)
        if settings.environment == "development":
            async with get_db() as session:
                await user_service.ensure_default_admin(session)
                logger.info("Default admin user ensured")
    except asyncio.TimeoutError:
        logger.error("PostgreSQL init TIMED OUT after 15s — auth will NOT work!")
    except Exception as e:
        logger.error("PostgreSQL initialization failed: %s", e)
        logger.error("Auth will NOT work without database!")

    elapsed = time.time() - startup_start
    logger.info("=== LIFESPAN READY in %.1fs — now serving requests ===", elapsed)

    yield

    # Shutdown
    await close_db()
    logger.info("PostgreSQL disconnected")
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ChampUTM API

    UTM parameter management and link tracking platform.

    ## Features

    - **Authentication**: User registration and JWT-based auth
    - **UTM Links**: Generate and manage UTM-tagged URLs (coming soon)
    - **Presets**: Save and reuse UTM templates (coming soon)
    - **Analytics**: Track link performance (coming soon)

    ## Authentication

    Use `/api/v1/auth/login` to get a JWT token.
    Include it in requests as: `Authorization: Bearer <token>`

    Development credentials:
    - Admin: `admin@champions.dev` / `admin123`
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
# In production, only allow requests from the frontend domain
# In development, allow localhost variants
allowed_origins = [settings.frontend_url]
if settings.environment == "development":
    allowed_origins.extend(
        [
            "http://localhost:3000",
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Accept"],
)

# Rate limiting
setup_rate_limiting(app)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root - returns basic info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(health.router)  # Health check at /health (no /api/v1 prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
