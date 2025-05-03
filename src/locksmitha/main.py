"""Main FastAPI application for login service using keylin and fastapi-users."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from keylin.auth import auth_backend, fastapi_users
from keylin.schemas import UserRead, UserCreate
from locksmitha.config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(title="Keylin Login Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserRead), prefix="/users", tags=["users"])

@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
