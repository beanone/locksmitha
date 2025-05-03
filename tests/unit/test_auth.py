import logging
from unittest.mock import MagicMock

import pytest

from locksmitha.auth import UserManager


@pytest.fixture
def user():
    mock_user = MagicMock()
    mock_user.id = 123
    return mock_user


@pytest.mark.asyncio
async def test_on_after_login(user, caplog):
    manager = UserManager(None)
    with caplog.at_level(logging.INFO):
        await manager.on_after_login(user)
    assert "User login: id=123" in caplog.text


@pytest.mark.asyncio
async def test_on_after_register(user, caplog):
    manager = UserManager(None)
    with caplog.at_level(logging.INFO):
        await manager.on_after_register(user)
    assert "User registered: id=123" in caplog.text


@pytest.mark.asyncio
async def test_on_after_forgot_password(user, caplog):
    manager = UserManager(None)
    with caplog.at_level(logging.INFO):
        await manager.on_after_forgot_password(user, token="dummy")
    assert "Password reset requested: id=123" in caplog.text


@pytest.mark.asyncio
async def test_on_after_request_verify(user, caplog):
    manager = UserManager(None)
    with caplog.at_level(logging.INFO):
        await manager.on_after_request_verify(user, token="dummy")
    assert "Verification requested: id=123" in caplog.text


@pytest.mark.asyncio
async def test_get_user_manager():
    from unittest.mock import MagicMock

    from locksmitha.auth import get_user_manager

    mock_user_db = MagicMock()
    agen = get_user_manager(user_db=mock_user_db)
    manager = await agen.__anext__()
    assert isinstance(manager, UserManager)
