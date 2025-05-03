# Locksmitha Login Service

A production-ready FastAPI login/authentication service for the beanone organization, modeled after the graph_reader_api project structure.

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

## Setup

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

## Running the Service

```bash
docker-compose up --build
```

Or locally:

```bash
uvicorn src.locksmitha.main:app --reload
```

## Testing

```bash
pytest
```

## Linting

```bash
pre-commit run --all-files
```

## CI/CD

- GitHub Actions for linting, testing, and Docker publishing are configured in `.github/workflows/`.

## License

MIT License