from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file.

    Attributes:
        JWT_SECRET: Secret key for JWT signing.
        DATABASE_URL: Database connection string.
        RESET_PASSWORD_SECRET: Secret for password reset tokens.
        VERIFICATION_SECRET: Secret for email verification tokens.
        allowed_origins: List of allowed CORS origins.
        JWT_ALGORITHM: Algorithm for JWT signing.
    """
    JWT_SECRET: str = "changeme"
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_SECONDS: int = 3600
    RESET_PASSWORD_SECRET: str | None = None
    VERIFICATION_SECRET: str | None = None
    allowed_origins: list[str] = Field(default_factory=list, alias="ALLOWED_ORIGINS")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> list[str]:
        """Parse allowed_origins from a string or list."""
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                v = v[1:-1]
            return [s.strip().strip('"').strip("'") for s in v.split(",") if s.strip()]
        return v

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.JWT_SECRET or self.JWT_SECRET == "changeme":
            raise RuntimeError("JWT_SECRET environment variable must be set")
        if self.RESET_PASSWORD_SECRET is None:
            self.RESET_PASSWORD_SECRET = self.JWT_SECRET
        if self.VERIFICATION_SECRET is None:
            self.VERIFICATION_SECRET = self.JWT_SECRET

settings = Settings()
