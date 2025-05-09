from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from keylin.auth import current_active_user
from keylin.db import get_async_session
from keylin.keylin_utils import create_api_key_record
from keylin.models import APIKey
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


class APIKeyCreateRequest(BaseModel):
    name: str | None = None
    service_id: str
    expires_at: datetime | None = None

class APIKeyReadResponse(BaseModel):
    id: str
    name: str | None
    service_id: str
    status: str
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None

class APIKeyCreateResponse(APIKeyReadResponse):
    plaintext_key: str

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

@router.post("/", response_model=APIKeyCreateResponse,
             status_code=status.HTTP_201_CREATED)
async def create_api_key(
    req: APIKeyCreateRequest,
    user=Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Create a new API key for the authenticated user."""
    user_id = str(user.id)
    plaintext_key, api_key_obj = create_api_key_record(
        user_id=user_id,
        service_id=req.service_id,
        name=req.name,
        expires_at=req.expires_at,
    )
    session.add(api_key_obj)
    await session.commit()
    await session.refresh(api_key_obj)
    return APIKeyCreateResponse(
        id=api_key_obj.id,
        name=api_key_obj.name,
        service_id=api_key_obj.service_id,
        status=api_key_obj.status,
        created_at=api_key_obj.created_at,
        expires_at=api_key_obj.expires_at,
        last_used_at=api_key_obj.last_used_at,
        plaintext_key=plaintext_key,
    )

@router.get("/", response_model=list[APIKeyReadResponse])
async def list_api_keys(
    user=Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all API keys for the authenticated user."""
    user_id = str(user.id)
    result = await session.execute(
        APIKey.__table__.select().where(APIKey.user_id == user_id)
    )
    keys = await result.fetchall()
    return [
        APIKeyReadResponse(
            id=row.id,
            name=row.name,
            service_id=row.service_id,
            status=row.status,
            created_at=row.created_at,
            expires_at=row.expires_at,
            last_used_at=row.last_used_at,
        )
        for row in keys
    ]

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    user=Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete (revoke) an API key by ID for the authenticated user."""
    user_id = str(user.id)
    result = await session.execute(
        APIKey.__table__.select().where(APIKey.id == key_id, APIKey.user_id == user_id)
    )
    row = await result.first()
    if not row:
        raise HTTPException(status_code=404, detail="API key not found")
    await session.execute(
        APIKey.__table__.delete().where(APIKey.id == key_id, APIKey.user_id == user_id)
    )
    await session.commit()
