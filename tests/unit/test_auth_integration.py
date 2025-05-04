
import pytest
from fastapi.testclient import TestClient

from src.locksmitha.main import app


@pytest.fixture(scope="function")
def httpserver_auth(httpserver):
    # Mock /auth/jwt/login endpoint
    httpserver.expect_request("/auth/jwt/login", method="POST").respond_with_json({
        "access_token": "testtoken",
        "token_type": "bearer"
    })
    # Mock /users/me endpoint (if you want to simulate the login service itself)
    httpserver.expect_request("/users/me", method="GET").respond_with_json({
        "email": "integration@example.com",
        "sub": "integration-test-user",
        "roles": ["admin"]
    })
    return httpserver

@pytest.fixture(scope="function")
def client(httpserver_auth, monkeypatch):
    # Patch the environment variable to use the mock server's URL
    monkeypatch.setenv("LOCKSMITHA_URL", httpserver_auth.url_for("/"))
    # Recreate the app with the new env var if needed
    return TestClient(app)

def test_integration_with_mock_login_service(client, httpserver_auth):
    # Simulate login to get a JWT
    login_response = client.post("/auth/jwt/login",
                                 json={"username": "u", "password": "p"})
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Use the JWT to call /users/me
    response = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "integration@example.com"
