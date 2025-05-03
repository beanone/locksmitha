"""App configuration and environment variable loading."""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    JWT_SECRET: str = os.getenv("KEYLIN_JWT_SECRET", "changeme")
    DATABASE_URL: str = os.getenv(
        "KEYLIN_DATABASE_URL", "sqlite+aiosqlite:///./test.db"
    )
    RESET_PASSWORD_SECRET: str = os.getenv("KEYLIN_RESET_PASSWORD_SECRET", JWT_SECRET)
    VERIFICATION_SECRET: str = os.getenv("KEYLIN_VERIFICATION_SECRET", JWT_SECRET)
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")


settings = Settings()
