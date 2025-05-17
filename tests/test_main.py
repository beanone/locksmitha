import pytest
from fastapi.testclient import TestClient

from src.login.main import app


@pytest.mark.asyncio
async def test_lifespan_coverage_async():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
