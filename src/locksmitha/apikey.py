from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from keylin.apikey_manager import create_api_key as handler_create_api_key
from keylin.apikey_manager import delete_api_key as handler_delete_api_key
from keylin.apikey_manager import list_api_keys as handler_list_api_keys
from keylin.auth import current_active_user
from keylin.db import get_async_session
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
    result = await handler_create_api_key(
        user_id=user_id,
        service_id=req.service_id,
        session=session,
        name=req.name,
        expires_at=req.expires_at,
    )
    return APIKeyCreateResponse(**result)

@router.get("/", response_model=list[APIKeyReadResponse])
async def list_api_keys(
    user=Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """List all API keys for the authenticated user."""
    user_id = str(user.id)
    keys = await handler_list_api_keys(user_id=user_id, session=session)
    return [APIKeyReadResponse(**k) for k in keys]

@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    user=Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    """Delete (revoke) an API key by ID for the authenticated user."""
    user_id = str(user.id)
    deleted = await handler_delete_api_key(key_id=key_id, user_id=user_id,
                                           session=session)
    if not deleted:
        raise HTTPException(status_code=404, detail="API key not found")
