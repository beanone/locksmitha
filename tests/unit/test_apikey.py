from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from keylin.db import get_async_session as keylin_get_async_session
from keylin.models import APIKey
from sqlalchemy.ext.asyncio import AsyncSession

from src.locksmitha.apikey import current_active_user
from src.locksmitha.main import app


@pytest.fixture(autouse=True)
def ensure_in_memory_db(monkeypatch):
    """Ensure DATABASE_URL is set to in-memory SQLite for these unit tests."""
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
def fake_user():
    class User:
        id = "user-123"
    return User()

@pytest.fixture
def fake_api_key_instance():
    return APIKey(
        user_id="user-123",
        key_hash="fake_hashed_key",
        service_id="svc",
        name="test key",
        status="active",
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(days=1),
        last_used_at=None,
        id="key-1"
    )

@pytest.mark.anyio
@patch("keylin.apikey_manager.create_api_key_record")
async def test_create_api_key(mock_create_api_key_record,
                              fake_user, fake_api_key_instance):
    app.dependency_overrides[current_active_user] = lambda: fake_user

    mock_db_session = AsyncMock(spec=AsyncSession)
    mock_db_session.add = Mock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()
    app.dependency_overrides[keylin_get_async_session] = lambda: mock_db_session

    mock_create_api_key_record.return_value = \
        ("plaintext_example_key", fake_api_key_instance)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api-keys/",
                                 json={"service_id": "svc", "name": "test key"})

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == fake_api_key_instance.id
    assert data["plaintext_key"] == "plaintext_example_key"
    assert data["name"] == fake_api_key_instance.name
    mock_db_session.add.assert_called_once_with(fake_api_key_instance)
    mock_db_session.commit.assert_awaited_once()
    mock_db_session.refresh.assert_awaited_once_with(fake_api_key_instance)

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_list_api_keys(fake_user, fake_api_key_instance):
    app.dependency_overrides[current_active_user] = lambda: fake_user

    mock_db_session = AsyncMock(spec=AsyncSession)
    mock_execute_result = AsyncMock()
    mock_execute_result.fetchall = AsyncMock(return_value=[fake_api_key_instance])
    mock_db_session.execute = AsyncMock(return_value=mock_execute_result)
    app.dependency_overrides[keylin_get_async_session] = lambda: mock_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api-keys/")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == fake_api_key_instance.id
    assert data[0]["name"] == fake_api_key_instance.name
    mock_db_session.execute.assert_awaited_once()

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_delete_api_key_success(fake_user, fake_api_key_instance):
    app.dependency_overrides[current_active_user] = lambda: fake_user

    mock_db_session = AsyncMock(spec=AsyncSession)
    mock_execute_result_first = AsyncMock()
    mock_execute_result_first.first.return_value = fake_api_key_instance
    mock_db_session.execute = AsyncMock(side_effect=[
        mock_execute_result_first,
        AsyncMock()
    ])
    mock_db_session.commit = AsyncMock()
    app.dependency_overrides[keylin_get_async_session] = lambda: mock_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete(f"/api-keys/{fake_api_key_instance.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert mock_db_session.execute.call_count == 2
    mock_db_session.commit.assert_awaited_once()

    app.dependency_overrides = {}

@pytest.mark.anyio
async def test_delete_api_key_not_found(fake_user):
    app.dependency_overrides[current_active_user] = lambda: fake_user

    mock_db_session = AsyncMock(spec=AsyncSession)
    mock_execute_result_first = AsyncMock()
    mock_execute_result_first.first.return_value = None
    mock_db_session.execute = AsyncMock(return_value=mock_execute_result_first)
    app.dependency_overrides[keylin_get_async_session] = lambda: mock_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/api-keys/non_existent_key_id")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "API key not found"
    mock_db_session.execute.assert_awaited_once()

    app.dependency_overrides = {}
