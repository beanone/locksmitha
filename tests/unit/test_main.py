from unittest.mock import Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from keylin.models import Base

from src.locksmitha.main import app, lifespan


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_lifespan_creates_tables():
    """Test that lifespan calls Base.metadata.create_all."""
    with patch.object(Base.metadata, "create_all",
                      new_callable=Mock) as mock_create_all:
        app = FastAPI()
        cm = lifespan(app)
        await cm.__aenter__()
        assert mock_create_all.call_count == 1
        await cm.__aexit__(None, None, None)
