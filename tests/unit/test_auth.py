import logging
from unittest.mock import MagicMock, patch

import pytest

from login.auth import UserManager


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
    assert f"User {user.id} logged in" in caplog.text


@pytest.mark.asyncio
async def test_on_after_register(user, caplog):
    manager = UserManager(None)
    with caplog.at_level(logging.INFO):
        await manager.on_after_register(user)
    assert "User registered: id=123" in caplog.text


@pytest.mark.asyncio
async def test_on_after_forgot_password(user):
    manager = UserManager(None)
    user.email = "test@example.com"
    token = "dummy-token"
    expected_link = f"{manager.settings.frontend_url}/reset-password?token={token}"
    with patch("login.auth.send_email") as mock_send_email:
        await manager.on_after_forgot_password(user, token=token)
        mock_send_email.assert_called_once_with(
            to_email="test@example.com",
            subject="Password Reset",
            body=f"Click the link to reset your password: {expected_link}",
        )


@pytest.mark.asyncio
async def test_on_after_request_verify(user):
    manager = UserManager(None)
    user.email = "test@example.com"
    token = "dummy-token"
    expected_link = f"{manager.settings.frontend_url}/verify-email?token={token}"
    with patch("login.auth.send_email") as mock_send_email:
        await manager.on_after_request_verify(user, token=token)
        mock_send_email.assert_called_once_with(
            to_email="test@example.com",
            subject="Verify Your Email",
            body=f"Click the link to verify your email: {expected_link}",
        )


@pytest.mark.asyncio
async def test_get_user_manager():
    from unittest.mock import MagicMock

    from login.auth import get_user_manager

    mock_user_db = MagicMock()
    agen = get_user_manager(user_db=mock_user_db)
    manager = await agen.__anext__()
    assert isinstance(manager, UserManager)
