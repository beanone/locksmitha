# Locksmitha Deployment Examples

This guide provides practical examples for deploying the Locksmitha login service using Docker. It covers different ways to pass environment variables (via `.env` files) and user databases (Postgres and SQLite) for both development and production scenarios.

---

## 1. Passing Environment Variables

### **A. Using Docker Compose (Recommended for Most Users)**

Docker Compose automatically loads environment variables from a `.env` file in the same directory as your `docker-compose.yml`:

```yaml
docker-compose.yml:

version: '3.8'
services:
  locksmitha:
    build: .
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: userdb
    ports:
      - "5432:5432"
```

**.env Example:**
```env
JWT_SECRET=supersecretjwtkey
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/userdb
RESET_PASSWORD_SECRET=supersecretresetkey
VERIFICATION_SECRET=supersecretverifykey
ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
```

---

### **B. Using `docker run` with `--env-file`**

If you want to run the container directly, pass the `.env` file using `--env-file`:

```bash
docker build -t locksmitha .
docker run --env-file .env -p 8000:8000 locksmitha
```

- Ensure `.env` is in your current directory or provide the full path.
- You can override any variable at runtime with `-e VAR=value`.

---

## 2. Passing the User Database

### **A. Using Postgres (Recommended for Production)**

- Configure your `.env` with the Postgres connection string:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/userdb
```

- With Docker Compose, the database is managed as a separate service (see above).
- For production, use managed Postgres or a secure, persistent volume.

---

### **B. Using SQLite (For Development or Testing)**

#### **i. Default (Ephemeral) SQLite**

- Set in `.env`:
  ```env
  DATABASE_URL=sqlite+aiosqlite:///./test.db
  ```
- The database will be created inside the container and lost when the container is removed.

#### **ii. Mounting a Pre-Populated SQLite DB**

- Copy your pre-populated DB to the host, then mount it into the container:

```bash
docker run --env-file .env \
  -v /path/on/host/my_prepopulated.db:/app/my_prepopulated.db \
  -e DATABASE_URL=sqlite+aiosqlite:///./my_prepopulated.db \
  -p 8000:8000 locksmitha
```

- This allows you to persist or reuse user data across container restarts.

---

## 3. Overriding Environment Variables at Runtime

You can override any variable from `.env` by passing `-e` flags:

```bash
docker run --env-file .env -e JWT_SECRET=anothersecret -p 8000:8000 locksmitha
```

---

## 4. Best Practices

- **Never commit secrets or production databases to version control.**
- Use strong, unique secrets for all environment variables.
- For production, use managed databases and secret managers where possible.
- Always validate your environment variables at application startup.

---

## 5. Environment Variables for Integrated Services

When deploying Locksmitha alongside other services (such as your main application), **each service should have its own `.env` file** with only the variables relevant to that service.

- The login service (`locksmitha`) is typically run from a published Docker image (e.g., via `docker pull hongyanworkshop123/locksmitha:latest`). You provide its `.env` file at runtime using `--env-file` or Docker Compose.
- The integrating service (e.g., your main FastAPI app) may be:
  - Run from a pulled Docker image (with its own `.env` file), **or**
  - Run from local source code (with a local `.env` file loaded by your process manager or framework).

**Example directory structure:**
```
project-root/
├── locksmitha.env         # For the login service (used with docker run --env-file)
├── myapp/
│   ├── .env              # For your main app (local dev or docker)
│   └── ...
```

**Example: Running Both Services with Docker**

```bash
# Run the login service from a pulled image
# (locksmitha.env contains only login-service variables)
docker pull beanone/locksmitha:latest
docker run --env-file locksmitha.env -p 8000:8000 hongyanworkshop123/locksmitha:latest

# Run your integrating service from local source (using uvicorn, etc.)
cd myapp
source .venv/bin/activate  # if using a virtualenv
export $(grep -v '^#' .env | xargs)  # load .env variables
uvicorn myapp.main:app --reload

# OR run your integrating service from a Docker image
# (myapp/.env contains only app-specific variables)
docker build -t myapp .
docker run --env-file myapp/.env -p 9000:9000 myapp
```

**Important:**
- The value of `JWT_SECRET` must be identical in both `.env` files for JWT authentication to work.
- Do **not** share the entire `.env` file between services—only copy the necessary variables.
- Each service should only have the environment variables it needs for security and clarity.

---

For more details, see the main [README.md](../README.md) and [userdb documentation](https://github.com/beanone/userdb).
