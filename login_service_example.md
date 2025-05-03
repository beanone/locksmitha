# FastAPI Login Service Example with keylin and fastapi-users

This guide provides a complete, production-ready example of a login/authentication service using [keylin](https://github.com/beanone/keylin) and [fastapi-users](https://github.com/fastapi-users/fastapi-users).

---

## Project Structure

```
login_service/
├── app/
│   ├── main.py
│   ├── config.py
│   └── __init__.py
├── .env
├── requirements.txt
└── README.md
```

---

## 1. `requirements.txt`

```
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
SQLAlchemy>=2.0.0
asyncpg>=0.28.0
keylin
python-dotenv
python-jose[cryptography]
email-validator
fastapi-users[sqlalchemy]>=12.0.0
```

---

## 2. `.env` Example

```
KEYLIN_JWT_SECRET=supersecretjwtkey
KEYLIN_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/keylindb
KEYLIN_RESET_PASSWORD_SECRET=supersecretresetkey
KEYLIN_VERIFICATION_SECRET=supersecretverifykey
ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
```

---

## 3. `app/config.py`

```python
"""App configuration and environment variable loading."""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    JWT_SECRET: str = os.getenv("KEYLIN_JWT_SECRET", "changeme")
    DATABASE_URL: str = os.getenv("KEYLIN_DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    RESET_PASSWORD_SECRET: str = os.getenv("KEYLIN_RESET_PASSWORD_SECRET", JWT_SECRET)
    VERIFICATION_SECRET: str = os.getenv("KEYLIN_VERIFICATION_SECRET", JWT_SECRET)
    ALLOWED_ORIGINS: list[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")

settings = Settings()
```

---

## 4. `app/main.py`

```python
"""Main FastAPI application for login service using keylin and fastapi-users."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from keylin.auth import auth_backend, fastapi_users, get_user_manager
from keylin.schemas import UserRead, UserCreate
from keylin.db import get_async_session
from app.config import settings

app = FastAPI(title="Keylin Login Service", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication and user management routes
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

@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
```

---

## 5. `app/__init__.py`

```python
# This file can be left empty or used for app-level imports.
```

---

## 6. Database Setup

- **Production:** Use Alembic for migrations. Example:

```bash
alembic revision --autogenerate -m "create user table"
alembic upgrade head
```

- **Development/Quick Start:** Create tables programmatically:

```python
from keylin.models import Base
from sqlalchemy import create_engine
import os

engine = create_engine(os.getenv("KEYLIN_DATABASE_URL", "sqlite:///./test.db"))
Base.metadata.create_all(engine)
```

---

## 7. Running the Service

1. **Install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
2. **Set environment variables:**
    ```bash
    cp .env.example .env  # or edit .env directly
    ```
3. **Run database migrations or create tables.**
4. **Start the server:**
    ```bash
    uvicorn app.main:app --reload
    ```

---

## 8. Testing

- Use `pytest` for tests. Example test file:

```python
# tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

---

## 9. Security & Best Practices

- Always use strong, unique secrets in production.
- Restrict `ALLOWED_ORIGINS` to trusted domains.
- Deploy behind HTTPS (TLS proxy).
- Use Alembic for schema migrations.
- Log authentication events for auditing.
- Enable email verification and rate limiting as needed.

---

## 10. References
- [keylin documentation](https://github.com/beanone/keylin)
- [fastapi-users documentation](https://fastapi-users.github.io/fastapi-users/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)