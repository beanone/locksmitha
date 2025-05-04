<p align="center">
  <img src="https://raw.githubusercontent.com/beanone/locksmitha/refs/heads/main/docs/assets/logos/locksmitha.svg" alt="Locksmitha Login Service" width="100%">
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/beanone/locksmitha/blob/main/LICENSE)
[![Tests](https://github.com/beanone/locksmitha/actions/workflows/tests.yml/badge.svg)](https://github.com/beanone/locksmitha/actions?query=workflow%3Atests)
[![Coverage](https://codecov.io/gh/beanone/locksmitha/branch/main/graph/badge.svg)](https://codecov.io/gh/beanone/locksmitha)
[![Code Quality](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)
[![Security Scan](https://github.com/beanone/locksmitha/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/beanone/locksmitha/actions/workflows/docker-publish.yml)

A production-ready FastAPI login/authentication service for the beanone organization. **This project is a direct sequel to the [keylin](https://github.com/beanone/keylin/blob/main/README.md) library, providing a full-featured login API and user management backend.**

---

## Table of Contents

- [Overview & Architecture](#overview--architecture)
- [Project Structure](#project-structure)
- [Setup & Usage](#setup--usage)
- [Database Setup](#database-setup)
- [Endpoints & Behavior](#endpoints--behavior)
- [Integrating Your FastAPI Service with the Login Service](#integrating-your-fastapi-service-with-the-login-service)
- [CI/CD](#cicd)
- [License](#license)

---

## Overview & Architecture

Locksmitha implements a secure, extensible authentication and user management service using FastAPI, SQLAlchemy, and [keylin](https://github.com/beanone/keylin). It is designed to be the authentication backend for modern web applications and microservices.

**Key features:**
- JWT-based authentication
- User registration, login, and profile endpoints
- Password reset and email verification (if enabled)
- Security-compliant logging and rate limiting
- Ready for RBAC/permission extension
- Dockerized and CI/CD ready

### Architecture Diagram
```mermaid
graph TD
    %% Out-of-scope (future) components use dashed borders and gray color
    style UI stroke-dasharray: 5 5,stroke:#bbb,fill:#f9f9f9
    style APP stroke-dasharray: 5 5,stroke:#bbb,fill:#f9f9f9

    subgraph User Management UI [User Management UI]
        UI[User Management UI]
    end
    subgraph Application Service [Application Service]
        APP[App Service]
    end
    subgraph Locksmitha Login Service
        A[FastAPI + keylin]
        DB[(Postgres DB)]
    end
    UI -- REST/JSON --> A
    APP -- REST/JSON --> A
    A -- SQLAlchemy/asyncpg --> DB
```

---

## Project Structure

```
locksmitha/
├── src/locksmitha/
│   ├── main.py
│   ├── config.py
│   ├── auth.py
│   └── ...
├── tests/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements-test.txt
├── .pre-commit-config.yaml
├── .dockerignore
├── .gitignore
├── .coveragerc
└── README.md
```

---

## Setup & Usage

1. **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```
2. **Install dependencies:**
    ```bash
    pip install hatch
    hatch build
    pip install dist/*.whl
    pip install -r requirements-test.txt
    ```
3. **Configure environment variables:**
    - Create a `.env` file in the project root with the following variables:
      ```env
      KEYLIN_JWT_SECRET=supersecretjwtkey
      KEYLIN_DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/keylindb
      KEYLIN_RESET_PASSWORD_SECRET=supersecretresetkey
      KEYLIN_VERIFICATION_SECRET=supersecretverifykey
      ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
      ```

4. **Run the service:**
    ```bash
    docker-compose up --build
    # or
    uvicorn src.locksmitha.main:app --reload
    ```

5. **Testing:**
    ```bash
    pytest
    ```

6. **Linting:**
    ```bash
    pre-commit run --all-files
    ```

---

## Database Setup

Locksmitha uses PostgreSQL as its primary database. You must have a running Postgres instance before starting the service.

### 1. Create the Database (Postgres Example)

If you have Docker Compose set up, the database will be created automatically. For manual/local setup:

```bash
# Start Postgres (if not using Docker)
sudo service postgresql start

# Create a database and user
psql -U postgres
CREATE DATABASE keylindb;
CREATE USER locksmitha_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE keylindb TO locksmitha_user;
```

### 2. Configure the Connection String

Set the `KEYLIN_DATABASE_URL` environment variable in your `.env` file:

```env
KEYLIN_DATABASE_URL=postgresql+asyncpg://locksmitha_user:your_strong_password@localhost:5432/keylindb
```

### 3. Run Migrations

- **Production:** Use Alembic for schema migrations:
    ```bash
    alembic upgrade head
    ```
- **Development:** Tables can be created automatically on app startup (see `lifespan` in `main.py`).

### 4. Development vs. Production
- **Development:** You may use SQLite for quick local testing by setting `KEYLIN_DATABASE_URL=sqlite+aiosqlite:///./test.db`.
- **Production:** Always use PostgreSQL or another robust RDBMS. Run migrations and use strong, unique credentials.

### 5. Best Practices
- Use strong, unique passwords for database users.
- Restrict database network access to trusted hosts/services only.
- Always use migrations (Alembic) to manage schema changes.
- Regularly back up your database.
- Never run your application or database as a superuser.
- Rotate credentials and secrets periodically.

For more details, see the [keylin documentation](https://github.com/beanone/keylin) and your database provider's security guides.

### Using a Pre-Existing Database

If the configured database does not exist, Locksmitha will create a new one automatically (for example, by running migrations or creating tables on startup). However, if you want to use a database that already contains user data, you have several options:

#### 1. Package the Database with Your Docker Image (SQLite)
- For SQLite, you can copy your pre-populated `.db` file into the Docker image:
    ```dockerfile
    COPY ./my_prepopulated.db /app/my_prepopulated.db
    ```
- Set your `KEYLIN_DATABASE_URL` to point to this file:
    ```env
    KEYLIN_DATABASE_URL=sqlite+aiosqlite:///./my_prepopulated.db
    ```

#### 2. Mount the Database File or Directory (Recommended)
- For both SQLite and Postgres, you can mount a host directory or file into the container using Docker volumes:
    ```bash
    # For SQLite
    docker run -v /path/on/host/my_prepopulated.db:/app/my_prepopulated.db ...
    # For Postgres (mounting data directory, advanced)
    docker run -v /path/on/host/pgdata:/var/lib/postgresql/data ...
    ```
- This allows you to persist data or use a pre-existing database without rebuilding the image.

#### 3. Connect to an Existing Database Instance (Postgres)
- For Postgres, simply set your `KEYLIN_DATABASE_URL` to point to an existing database instance that already contains user data:
    ```env
    KEYLIN_DATABASE_URL=postgresql+asyncpg://user:password@host:5432/existing_db
    ```
- Ensure the user has the necessary privileges and the schema matches the expected structure.

#### 4. Permissions and Security
- When mounting or packaging databases, ensure the container has the correct file permissions to read/write the database.
- Never expose sensitive database files or credentials in public images or repositories.
- For production, prefer connecting to managed/external databases and use secure credentials.

For more details on Docker volumes, see the [Docker documentation](https://docs.docker.com/storage/volumes/). For database schema requirements, see the [keylin documentation](https://github.com/beanone/keylin).

---

## Endpoints & Behavior

| Endpoint                | Method | Auth Required | Description                        |
|------------------------|--------|--------------|------------------------------------|
| `/auth/jwt/login`      | POST   | No           | User login (returns JWT)           |
| `/auth/register`       | POST   | No           | User registration                  |
| `/users/me`            | GET    | Yes          | Get current user info              |
| `/users/`              | GET    | Yes (admin)  | List users (admin only)            |
| `/auth/forgot-password`| POST   | No           | Request password reset (if enabled)|
| `/auth/reset-password` | POST   | No           | Reset password (if enabled)        |
| `/auth/verify`         | POST   | No           | Email verification (if enabled)    |
| `/health`              | GET    | No           | Health check endpoint              |

- **Registration and login are open to all.**
- **User info and user listing require authentication (and admin for listing).**
- **Password reset and verification are optional, depending on config.**

- **Note:** The `/users/` endpoint is currently accessible to all authenticated users. Restriction to users with the "admin" role is planned for a future release, once role-based access control is implemented.

See [API_UI_INTEGRATION_GUIDE.md](./API_UI_INTEGRATION_GUIDE.md) for request/response examples and integration details.

---

## Environment Variables for Authentication Integration

To integrate with the Locksmitha login service, configure the following environment variables in your `.env`:

```env
LOCKSMITHA_URL=http://localhost:8001  # URL and port of the Locksmitha login service
KEYLIN_JWT_SECRET=changeme            # Must match the JWT secret used by Locksmitha
```

- `LOCKSMITHA_URL` is used to construct the OAuth2 token URL for authentication.
- `KEYLIN_JWT_SECRET` is used to validate JWTs issued by Locksmitha.

---

## Integrating Your FastAPI Service with the Login Service

To use Locksmitha as your authentication provider in another FastAPI application, follow these steps:

### 1. Authenticate Users via the Login Service
- Direct your frontend or API clients to the login service's `/auth/jwt/login` endpoint to obtain a JWT access token.
- Example request:
    ```http
    POST ${LOCKSMITHA_URL}/auth/jwt/login
    Content-Type: application/json
    {
      "username": "user@example.com",
      "password": "yourpassword"
    }
    ```
- The response will include an `access_token` (JWT) and `token_type`.

### 2. Use JWTs to Secure Your FastAPI Endpoints
- Require clients to include the JWT in the `Authorization: Bearer <token>` header for protected endpoints in your service.
- In your FastAPI app, validate the JWT using the same secret as the login service (from `KEYLIN_JWT_SECRET`).
- **Recommended setup:**
    ```python
    import os
    from fastapi.security import OAuth2PasswordBearer

    LOCKSMITHA_URL = os.getenv("LOCKSMITHA_URL", "http://localhost:8001")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{LOCKSMITHA_URL}/auth/jwt/login")
    # ... rest of your authentication dependency ...
    ```

### 3. Integration Options
- **In-Service Integration:**
  - Use the authentication dependency (`Depends(get_current_user)`) directly in your FastAPI endpoints.
  - Best for microservices or when you control the FastAPI codebase.
- **Out-of-Service Integration:**
  - Use an API gateway, reverse proxy, or external middleware to validate JWTs before requests reach your FastAPI app.
  - Best for legacy services, polyglot environments, or when you want to centralize auth logic.
- Choose the approach that best fits your deployment and security requirements.

### 4. Fetch User Info
- To get user details, call the login service's `/users/me` endpoint with the JWT:
    ```http
    GET ${LOCKSMITHA_URL}/users/me
    Authorization: Bearer <access_token>
    ```

### 5. Environment and Configuration
- Ensure your service has access to the login service's JWT secret (or public key if using asymmetric JWTs).
- Set CORS and network rules to allow communication between your service and the login service.
- Do **not** implement your own registration or password reset; delegate these to the login service endpoints.

### 6. Example Architecture
```
[Client] ──> [Your FastAPI Service] ──> [Locksmitha Login Service]
   |                |                        |
   |  (JWT Bearer)  |  (JWT validation)      |
   |                |                        |
   └───────────────>┴────────────────────────┘
```

For more advanced integration (e.g., OAuth2, SSO, or custom claims), refer to the [API_UI_INTEGRATION_GUIDE.md](./API_UI_INTEGRATION_GUIDE.md), [fastapi-users documentation](https://fastapi-users.github.io/fastapi-users/), and [keylin documentation](https://github.com/beanone/keylin).

---

## CI/CD

Locksmitha uses GitHub Actions for CI/CD. The workflow includes:
- Unit tests
- Code coverage
- Security scan
- Docker image build and push

---

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/beanone/locksmitha/blob/main/LICENSE) file for more details.
