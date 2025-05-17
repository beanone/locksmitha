import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_with_isolated_db(monkeypatch):
    # Create a temporary file for the DB
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name
        db_url = f"sqlite+aiosqlite:///{db_path}"

        # Set env vars for the test
        monkeypatch.setenv("DATABASE_URL", db_url)
        monkeypatch.setenv("JWT_SECRET", "test_jwt_secret")

        from src.locksmitha.main import create_app

        test_app = create_app()
        with TestClient(test_app) as client:
            # Test health endpoint
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

            # Test register endpoint
            response = client.post(
                "/auth/register", json={"email": "test@test.com", "password": "test"}
            )
            assert response.status_code == 201

            # Test login endpoint
            response = client.post(
                "/auth/jwt/login",
                data={"username": "test@test.com", "password": "test"},
            )
            assert response.status_code == 200
            token = response.json()["access_token"]

            # Test users/me endpoint
            response = client.get(
                "/users/me", headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200

        os.remove(db_path)
