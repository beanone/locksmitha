from keylin.config import Settings as KeylinSettings
from pydantic import Field


class Settings(KeylinSettings):
    postgres_user: str = Field(default="postgres",
                               json_schema_extra={"env": "POSTGRES_USER"})
    postgres_password: str = Field(default="password",
                                   json_schema_extra={"env": "POSTGRES_PASSWORD"})
    postgres_db: str = Field(default="keylindb",
                             json_schema_extra={"env": "POSTGRES_DB"})
    log_level: str = Field(default="INFO",
                           json_schema_extra={"env": "LOG_LEVEL"})
