from keylin.config import Settings as KeylinSettings
from pydantic import Field


class Settings(KeylinSettings):
    postgres_user: str = Field(default="postgres", env="POSTGRES_USER")
    postgres_password: str = Field(default="password", env="POSTGRES_PASSWORD")
    postgres_db: str = Field(default="keylindb", env="POSTGRES_DB")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
