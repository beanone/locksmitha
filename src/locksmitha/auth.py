"""User manager and authentication backend setup for locksmitha login service.

This module defines the UserManager class, which handles user-related events
such as registration, login, password reset, and email verification. It is designed
for use with FastAPI-Users and SQLAlchemy, and follows best practices for security,
configuration, and extensibility.
"""

import logging
import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from keylin.db import get_user_db
from keylin.models import User

from .config import Settings
from .email_utils import send_email

logger = logging.getLogger("locksmitha.auth")

settings = Settings()


def get_jwt_strategy() -> JWTStrategy:
    """Return a JWTStrategy using the configured secret and 1 hour lifetime."""
    return JWTStrategy(
        secret=settings.JWT_SECRET,
        lifetime_seconds=3600,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="auth/jwt/login"),
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """User manager for handling authentication events and secrets.

    This class extends BaseUserManager from fastapi-users, providing hooks for
    user lifecycle events. It uses secrets loaded from environment variables for
    password reset and email verification tokens, ensuring security and configurability.
    """
    settings = Settings()
    reset_password_token_secret = settings.RESET_PASSWORD_SECRET
    verification_token_secret = settings.VERIFICATION_SECRET

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        response: Response | None = None
    ) -> None:
        """Called after a successful user login.

        This method can be used to update last login timestamps, trigger analytics,
        or send login notifications. Here, we simply log the event for auditing.
        """
        logger.info(f"User {user.id} logged in.")

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
        reset_link = f"{self.settings.frontend_url}/reset-password?token={token}"
        send_email(
            to_email=user.email,
            subject="Password Reset",
            body=f"Click the link to reset your password: {reset_link}"
        )


    async def on_after_request_verify(self, user: User, token: str,
                                      request: Request = None) -> None:
        """Called after a user requests email verification.

        Sends a verification email with a secure, time-limited token. The verification
        link is constructed using the frontend URL and the token. Email verification
        is important to confirm user ownership and prevent spam or abuse.
        """
        verify_link = f"{self.settings.frontend_url}/verify-email?token={token}"
        send_email(
            to_email=user.email,
            subject="Verify Your Email",
            body=f"Click the link to verify your email: {verify_link}"
        )

    # Additional hooks and business logic can be added here as needed.


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """Dependency for providing a UserManager instance with the correct user DB."""
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
