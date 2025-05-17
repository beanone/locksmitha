# Docker Improvements

## Dockerfile Improvements

### Current Dockerfile:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY requirements-test.txt ./
COPY src/ src/
RUN pip install --upgrade pip setuptools
RUN pip install hatch hatchling
RUN hatch build && pip install dist/*.whl
RUN pip install -r requirements-test.txt

COPY . .

CMD ["uvicorn", "src.login.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Suggested Improvements:

1. **Use a Multi-Stage Build:**
   - Separate build and runtime stages to reduce the final image size.
   - Example:
     ```dockerfile
     FROM python:3.12-slim AS builder
     WORKDIR /app
     COPY pyproject.toml requirements-test.txt ./
     RUN pip install --upgrade pip setuptools hatch hatchling
     RUN hatch build

     FROM python:3.12-slim
     WORKDIR /app
     COPY --from=builder /app/dist/*.whl ./
     RUN pip install *.whl
     COPY . .
     CMD ["uvicorn", "src.login.main:app", "--host", "0.0.0.0", "--port", "8000"]
     ```

2. **Pin Dependencies:**
   - Since `pip freeze` is not suitable for development environments, manually create a `requirements.txt` with pinned versions.
   - Example:
     ```dockerfile
     COPY requirements.txt .
     RUN pip install -r requirements.txt
     ```

3. **Use a Non-Root User:**
   - Run the application as a non-root user for security.
   - Example:
     ```dockerfile
     RUN adduser --disabled-password --gecos "" appuser
     USER appuser
     ```

4. **Optimize Layer Caching:**
   - Copy only necessary files before installing dependencies.
   - The second `COPY . .` is mainly for bringing in the `.env` file, which may not exist on a new developer's machine.
   - Example:
     ```dockerfile
     COPY pyproject.toml requirements.txt ./
     RUN pip install -r requirements.txt
     COPY . .
     ```

5. **Use .dockerignore:**
   - Create a `.dockerignore` file to exclude unnecessary files (e.g., `.git`, `__pycache__`, etc.).

## docker-compose.yml Improvements

### Current docker-compose.yml:
```yaml
version: '3.8'
services:
  login:
    build: .
    command: uvicorn src.login.main:app --host 0.0.0.0 --port 8001 --reload
    ports:
      - "8001:8001"
    env_file:
      - .env
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

### Suggested Improvements:

1. **Use Environment Variables for Secrets:**
   - Avoid hardcoding sensitive data (e.g., `POSTGRES_PASSWORD`).
   - Use a `.env` file or Docker secrets for production.

2. **Add Health Checks:**
   - Ensure the database is ready before starting the app.
   - Example:
     ```yaml
     depends_on:
       db:
         condition: service_healthy
     healthcheck:
       test: ["CMD-SHELL", "pg_isready -U postgres"]
       interval: 5s
       timeout: 5s
       retries: 5
     ```

3. **Use Named Volumes for Persistence:**
   - Ensure database data persists across container restarts.
   - Example:
     ```yaml
     volumes:
       - postgres_data:/var/lib/postgresql/data
     volumes:
       postgres_data:
     ```

4. **Limit Resource Usage:**
   - Add resource limits to prevent container overuse.
   - Example:
     ```yaml
     deploy:
       resources:
         limits:
           cpus: '0.5'
           memory: 512M
     ```

5. **Use a Specific Network:**
   - Define a custom network for better isolation.
   - Example:
     ```yaml
     networks:
       - app_network
     networks:
       app_network:
     ```

## Summary Table

| Improvement                | Dockerfile | docker-compose.yml |
|----------------------------|------------|-------------------|
| Multi-Stage Build          | ✅          | N/A               |
| Pin Dependencies           | ✅          | N/A               |
| Non-Root User              | ✅          | N/A               |
| Optimize Layer Caching     | ✅          | N/A               |
| Use .dockerignore          | ✅          | N/A               |
| Environment Variables      | N/A         | ✅                |
| Health Checks              | N/A         | ✅                |
| Named Volumes              | N/A         | ✅                |
| Resource Limits            | N/A         | ✅                |
| Custom Network             | N/A         | ✅                |

## Next Steps

- Implement the suggested improvements in your Dockerfile and docker-compose.yml.
- Test the changes locally and in CI to ensure everything works as expected.
