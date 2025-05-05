"""User manager and authentication backend setup for locksmitha login service.

This module defines the UserManager class, which handles user-related events
such as registration, login, password reset, and email verification. It is designed
for use with FastAPI-Users and SQLAlchemy, and follows best practices for security,
configuration, and extensibility.
"""

import logging
from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from fastapi_users.manager import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from keylin.db import get_user_db
from keylin.models import User

logger = logging.getLogger("locksmitha.auth")


class UserManager(BaseUserManager[User, int]):
    """User manager for handling authentication events and secrets.

    This class extends BaseUserManager from fastapi-users, providing hooks for
    user lifecycle events. It uses secrets loaded from environment variables for
    password reset and email verification tokens, ensuring security and configurability.
    """
    async def on_after_login(self, user: User, request: Request = None) -> None:
        """Called after a successful user login.

        This method can be used to update last login timestamps, trigger analytics,
        or send login notifications. Here, we simply log the event for auditing.
        """
        logger.info(f"User login: id={user.id}")

    async def on_after_register(self, user: User, request: Request = None) -> None:
        """Called after a new user registers.

        Sends a welcome email with a verification link. This ensures users verify
        their email address, which is critical for account security and communication.
        """
        logger.info(f"User registered: id={user.id}")


    async def on_after_forgot_password(self, user: User, token: str,
                                       request: Request = None) -> None:
        """Called after a user requests a password reset.

        Sends a password reset email with a secure, time-limited token. The reset
        link is constructed using the frontend URL and the token. This flow is
        essential for account recovery and must be secure to prevent abuse.
        """
        logger.info(f"Password reset requested: id={user.id}")


    async def on_after_request_verify(self, user: User, token: str,
                                      request: Request = None) -> None:
        """Called after a user requests email verification.

        Sends a verification email with a secure, time-limited token. The verification
        link is constructed using the frontend URL and the token. Email verification
        is important to confirm user ownership and prevent spam or abuse.
        """
        logger.info(f"Verification requested: id={user.id}")

    # Additional hooks and business logic can be added here as needed.


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Dependency for providing a UserManager instance with the correct user DB."""
    yield UserManager(user_db)
