# Keylin Login Service

A production-ready FastAPI login/authentication service using [keylin](https://github.com/beanone/keylin) and [fastapi-users](https://github.com/fastapi-users/fastapi-users).

## Project Structure

```
locksmitha/
├── main.py
├── config.py
├── __init__.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Setup

1. **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Configure environment variables:**
    - Create a `.env` file in the project root with the following variables:
      ```env
      KEYLIN_JWT_SECRET=supersecretjwtkey
      KEYLIN_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/keylindb
      KEYLIN_RESET_PASSWORD_SECRET=supersecretresetkey
      KEYLIN_VERIFICATION_SECRET=supersecretverifykey
      ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
      ```

## Database Setup

- **Production:** Use Alembic for migrations.
- **Development:** You can create tables programmatically using SQLAlchemy and keylin models.

## Running the Service

```bash
uvicorn locksmitha.main:app --reload
```

## Endpoints

- `POST /auth/jwt/login` — Login
- `POST /auth/register` — Register
- `GET /users/me` — Get current user
- `GET /health` — Health check

## Security & Best Practices

- Use strong, unique secrets in production.
- Restrict `ALLOWED_ORIGINS` to trusted domains.
- Deploy behind HTTPS.
- Use Alembic for schema migrations.
- Log authentication events for auditing.
- Enable email verification and rate limiting as needed.

## References
- [keylin documentation](https://github.com/beanone/keylin)
- [fastapi-users documentation](https://fastapi-users.github.io/fastapi-users/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)