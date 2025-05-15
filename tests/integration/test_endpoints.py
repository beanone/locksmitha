"""Integration tests for the FastAPI application."""

import os
import tempfile

from fastapi.testclient import TestClient


def test_with_isolated_db(monkeypatch):  # noqa: PLR0915
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

            # Test API key creation
            response = client.post(
                "/api-keys/",
                json={"service_id": "test-service", "name": "Test Key"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 201
            key_data = response.json()
            assert "plaintext_key" in key_data
            api_key = key_data["plaintext_key"]

            # Test API key authentication
            response = client.get(
                "/auth/api-key/me",
                headers={"X-API-Key": api_key},
            )
            assert response.status_code == 200
            user_data = response.json()
            assert user_data["email"] == "test@test.com"
            assert user_data["is_active"] is True

            # Test API key listing
            response = client.get(
                "/api-keys/",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200
            keys = response.json()
            assert len(keys) == 1
            assert keys[0]["name"] == "Test Key"

            # Test API key deletion
            response = client.delete(
                f"/api-keys/{keys[0]['id']}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 204

            # Verify API key no longer works
            response = client.get(
                "/auth/api-key/me",
                headers={"X-API-Key": api_key},
            )
            assert response.status_code == 401

            # Test invalid API key
            response = client.get(
                "/auth/api-key/me",
                headers={"X-API-Key": "invalid-key"},
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid API key"

            # Test missing API key
            response = client.get("/auth/api-key/me")
            assert response.status_code == 403

            # Create a new user and deactivate them
            response = client.post(
                "/auth/register",
                json={"email": "inactive@test.com", "password": "test"},
            )
            assert response.status_code == 201

            # Login as the new user
            response = client.post(
                "/auth/jwt/login",
                data={"username": "inactive@test.com", "password": "test"},
            )
            assert response.status_code == 200
            inactive_token = response.json()["access_token"]

            # Get the user's ID for admin operations
            response = client.get(
                "/users/me", headers={"Authorization": f"Bearer {inactive_token}"}
            )
            assert response.status_code == 200
            inactive_user_id = response.json()["id"]

            # Create API key for inactive user
            response = client.post(
                "/api-keys/",
                json={"service_id": "test-service", "name": "Inactive User Key"},
                headers={"Authorization": f"Bearer {inactive_token}"},
            )
            assert response.status_code == 201
            inactive_key = response.json()["plaintext_key"]

            # Log in as admin
            response = client.post(
                "/auth/jwt/login",
                data={"username": "keylin@locksmitha.com", "password": "locksmitha"},
            )
            assert response.status_code == 200
            admin_token = response.json()["access_token"]

            # Deactivate the user as admin
            response = client.patch(
                f"/users/{inactive_user_id}",
                json={
                    "id": inactive_user_id,
                    "user_id_str": str(inactive_user_id),
                    "email": "inactive@test.com",
                    "is_active": False,
                    "is_superuser": False,
                    "is_verified": False,
                    "full_name": None,
                },
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert response.status_code == 200

            # Verify API key doesn't work for inactive user
            response = client.get(
                "/auth/api-key/me",
                headers={"X-API-Key": inactive_key},
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "User not found or inactive"

            # Delete the user as admin
            response = client.delete(
                f"/users/{inactive_user_id}",
                headers={"Authorization": f"Bearer {admin_token}"},
            )
            assert response.status_code == 204

            # Verify API key doesn't work for deleted user
            response = client.get(
                "/auth/api-key/me",
                headers={"X-API-Key": inactive_key},
            )
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid API key"

        os.remove(db_path)
