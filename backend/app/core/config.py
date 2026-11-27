"""Backend configuration module (PostgreSQL, Security, Timezone & Currency)."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    app_name: str = os.getenv("APP_NAME", "MockProject_Group7")
    app_env: str = os.getenv("APP_ENV", "development")
    app_timezone: str = os.getenv("APP_TIMEZONE", "Asia/Ho_Chi_Minh")
    app_currency: str = os.getenv("APP_CURRENCY", "VND")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/mockproject_group7_db",
    )
    session_idle_timeout_minutes: int = int(os.getenv("SESSION_IDLE_TIMEOUT_MINUTES", "30"))
    upload_max_size_mb: int = int(os.getenv("UPLOAD_MAX_SIZE_MB", "5"))


settings = Settings()
