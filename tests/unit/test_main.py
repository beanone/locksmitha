from contextlib import asynccontextmanager
from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from keylin.models import Base
from sqlalchemy.ext.asyncio import create_async_engine

from src.locksmitha.config import Settings
from src.locksmitha.main import create_app


def test_health_endpoint():
    app = create_app()
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_lifespan_creates_tables(monkeypatch):
    """Test that lifespan calls Base.metadata.create_all."""
    with patch.object(
        Base.metadata, "create_all", new_callable=Mock
    ) as mock_create_all:
        # Patch the database URL to use SQLite for this test
        monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

        @asynccontextmanager
        async def test_lifespan(app):
            settings = Settings()
            engine = create_async_engine(settings.DATABASE_URL, echo=True)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            yield

        app = FastAPI(lifespan=test_lifespan)
        cm = app.router.lifespan_context(app)
        await cm.__aenter__()
        assert mock_create_all.call_count == 1
        await cm.__aexit__(None, None, None)
