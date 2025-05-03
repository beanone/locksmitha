"""User manager and authentication backend setup for locksmitha login service."""
from typing import AsyncGenerator
from keylin.db import get_user_db
from keylin.models import User
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = "changeme"
    verification_token_secret = "changeme"

    # Add custom logic if needed

async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)