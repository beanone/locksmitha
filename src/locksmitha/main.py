"""Main FastAPI application for login service using keylin and fastapi-users."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from keylin import db
from keylin.auth import auth_backend, fastapi_users
from keylin.schemas import UserCreate, UserRead

from . import apikey
from .config import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def create_app() -> FastAPI:
    """App factory for FastAPI application."""
    settings = Settings()
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Automatically create tables if they do not exist (dev/CI only)
        async with db.lifespan():
            yield

    app = FastAPI(title="Keylin Login Service", version="1.0.0", lifespan=lifespan)

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserRead),
        prefix="/users",
        tags=["users"],
    )
    app.include_router(apikey.router)

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "ok"}

    return app

app = create_app()
