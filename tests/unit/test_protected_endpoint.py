"""Sample integration test showing how to use keylin.jwt_utils in any FastAPI app.

This test demonstrates:
1. How to protect a FastAPI endpoint with JWT authentication
2. How to test the endpoint using keylin.jwt_utils
3. How to handle different authentication scenarios
"""

import os
from typing import Annotated
from uuid import UUID

import jwt
import pytest
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import AsyncClient
from keylin.config import JWT_ALGORITHM, JWT_SECRET
from keylin.jwt_utils import create_jwt_for_user

# --- FastAPI App Setup ---

app = FastAPI()
security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> UUID:
    """Validate JWT and return user ID."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return UUID(payload["sub"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e!s}",
        ) from e

@app.get("/protected")
async def protected_endpoint(user_id: Annotated[UUID, Depends(get_current_user)]):
    """Example protected endpoint that requires JWT authentication."""
    return {"message": f"Hello, user {user_id}!"}

# --- Tests ---

@pytest.fixture
async def client():
    """Create a test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
def set_jwt_secret():
    """Set the JWT secret for testing."""
    os.environ["KEYLIN_JWT_SECRET"] = "test_secret"
    yield
    del os.environ["KEYLIN_JWT_SECRET"]

async def test_protected_endpoint_with_valid_jwt(client: AsyncClient):
    """Test that a valid JWT allows access to the protected endpoint."""
    # Create a JWT for a test user
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    jwt = create_jwt_for_user(user_id, "test@example.com")

    # Make request with JWT
    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {jwt}"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Hello, user {user_id}!"}

async def test_protected_endpoint_without_jwt(client: AsyncClient):
    """Test that the endpoint rejects requests without a JWT."""
    response = await client.get("/protected")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"

async def test_protected_endpoint_with_invalid_jwt(client: AsyncClient):
    """Test that the endpoint rejects requests with an invalid JWT."""
    response = await client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]

async def test_protected_endpoint_with_expired_jwt(client: AsyncClient):
    """Test that the endpoint rejects requests with an expired JWT."""
    # Create an expired JWT
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    jwt = create_jwt_for_user(user_id, "test@example.com", expires_seconds=-1)

    response = await client.get(
        "/protected",
        headers={"Authorization": f"Bearer {jwt}"}
    )
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]
