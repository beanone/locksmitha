import os
import tempfile
import uuid

import pytest
from keylin.models import Base, User
from passlib.hash import argon2
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture(scope="function")
def isolated_test_db(monkeypatch):
    # Create a temporary file for the DB
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name
    db_url = f"sqlite+aiosqlite:///{db_path}"

    # Seed the DB
    async def seed():
        engine = create_async_engine(db_url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            user = User(
                id=uuid.uuid4(),
                email="testuser@example.com",
                hashed_password=argon2.hash("testpassword123"),
                is_active=True,
                is_superuser=False,
                is_verified=False,
                full_name="Integration Test User"
            )
            session.add(user)
            await session.commit()
    import asyncio
    asyncio.run(seed())

    # Set env vars for the test
    monkeypatch.setenv("KEYLIN_DATABASE_URL", db_url)
    monkeypatch.setenv("KEYLIN_JWT_SECRET", "test_jwt_secret")
    yield db_url

    # Cleanup
    os.remove(db_path)

@pytest.mark.asyncio
async def test_integration_with_mock_login_service(isolated_test_db):
    import httpx
    from httpx import ASGITransport

    from locksmitha.main import app

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Simulate login to get a JWT
        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "testuser@example.com", "password": "testpassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200, login_response.text
        token = login_response.json()["access_token"]

        # Use the JWT to call /users/me
        response = await client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["email"] == "testuser@example.com"
