"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""

from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "ChampUTM"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"

    # API
    api_v1_prefix: str = "/api/v1"

    # PostgreSQL (User Management & Data Persistence)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "champutm"
    postgres_password: str = "champutm_dev"
    postgres_db: str = "champutm"
    database_url: str = ""  # Railway: set DATABASE_URL to override individual vars

    # JWT Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440  # 24 hours

    # Security
    frontend_url: str = "http://localhost:3000"  # Frontend URL for CORS

    # GeoIP (MaxMind GeoLite2)
    geoip_db_path: str = "/app/geoip/GeoLite2-City.mmdb"

    # VPN detection via ip-api.com (free, best-effort)
    vpn_detection_enabled: bool = True

    @property
    def postgres_url(self) -> str:
        """Build PostgreSQL async connection URL."""
        if self.database_url:
            url = self.database_url
            # Railway may provide postgres:// or postgresql://, normalize to asyncpg scheme
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    def validate_production_settings(self) -> None:
        """
        Validate critical settings for non-development deployment.
        Raises ValueError if any critical settings are using default/insecure values.
        """
        if self.environment == "development":
            return

        errors = []

        # Check JWT secret
        if self.jwt_secret_key == "your-secret-key-change-in-production":
            errors.append("JWT_SECRET_KEY must be changed from default value")

        if len(self.jwt_secret_key) < 32:
            errors.append("JWT_SECRET_KEY must be at least 32 characters long")

        # Check database password (skip if DATABASE_URL is provided)
        if not self.database_url and (
            not self.postgres_password or self.postgres_password == "champutm_dev"
        ):
            errors.append("POSTGRES_PASSWORD must be set to a secure value")

        # Debug must be off
        if self.debug:
            errors.append("DEBUG must be False outside development")

        # Frontend URL must not be localhost
        if "localhost" in self.frontend_url or "127.0.0.1" in self.frontend_url:
            errors.append("FRONTEND_URL must not be localhost outside development")

        if errors:
            raise ValueError(
                "Configuration validation failed:\n"
                + "\n".join(f"  - {error}" for error in errors)
            )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
