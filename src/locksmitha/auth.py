"""User manager and authentication backend setup for locksmitha login service."""
import logging
from typing import AsyncGenerator
from keylin.db import get_user_db
from keylin.models import User
from fastapi_users.manager import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi import Depends

logger = logging.getLogger("locksmitha.auth")

class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = "changeme"
    verification_token_secret = "changeme"

    async def on_after_login(self, user: User, request=None):
        logger.info(f"User login: id={user.id}")

    async def on_after_register(self, user: User, request=None):
        logger.info(f"User registered: id={user.id}")

    async def on_after_forgot_password(self, user: User, token: str, request=None):
        logger.info(f"Password reset requested: id={user.id}")

    async def on_after_request_verify(self, user: User, token: str, request=None):
        logger.info(f"Verification requested: id={user.id}")

    # Add custom logic if needed

async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)