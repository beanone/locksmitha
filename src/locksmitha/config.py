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
    smtp_host: str = Field(default="localhost",
                           json_schema_extra={"env": "SMTP_HOST"})
    smtp_port: int = Field(default=1025,
                           json_schema_extra={"env": "SMTP_PORT"})
    smtp_user: str = Field(default="",
                           json_schema_extra={"env": "SMTP_USER"})
    smtp_password: str = Field(default="",
                              json_schema_extra={"env": "SMTP_PASSWORD"})
    smtp_tls: bool = Field(default=False,
                          json_schema_extra={"env": "SMTP_TLS"})
    frontend_url: str = Field(default="http://localhost:3000",
                              json_schema_extra={"env": "FRONTEND_URL"})
