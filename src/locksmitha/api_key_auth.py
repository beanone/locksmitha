"""API key authentication implementation for FastAPI.

This module provides API key authentication functionality using FastAPI's dependency
injection system. It includes models for API key validation and a router for API key
authentication endpoints.
"""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from keylin.db import get_async_session
from keylin.keylin_utils import hash_api_key
from keylin.models import APIKey, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key")

router = APIRouter(prefix="/auth/api-key", tags=["auth"])


async def get_user_by_api_key_dependency(
    api_key: str = Security(api_key_header),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Get user by API key from header.

    Args:
        api_key: The API key from the X-API-Key header
        session: Database session

    Returns:
        User: User associated with the API key

    Raises:
        HTTPException: 401 if API key is invalid
    """
    # Hash the incoming API key
    key_hash = hash_api_key(api_key)

    # Look up the API key record
    result = await session.execute(
        select(APIKey).where(APIKey.key_hash == key_hash, APIKey.status == "active")
    )
    api_key_record = result.scalar_one_or_none()

    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Get the associated user using user_id_str
    print(
        "DEBUG: Looking up user with user_id_str:", api_key_record.user_id
    )  # Debug log
    result = await session.execute(
        select(User).where(User.user_id_str == api_key_record.user_id)
    )
    user = result.scalar_one_or_none()
    print("DEBUG: User lookup result:", user is not None)  # Debug log

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Update last_used_at
    api_key_record.last_used_at = datetime.now(UTC)
    await session.commit()

    return user


@router.get("/me")
async def get_current_user(
    user: Annotated[User, Depends(get_user_by_api_key_dependency)],
) -> dict:
    """Get current user information using API key.

    Args:
        user: User from API key dependency

    Returns:
        dict: User information
    """
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
    }
