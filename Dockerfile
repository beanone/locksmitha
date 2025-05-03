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

CMD ["uvicorn", "src.locksmitha.main:app", "--host", "0.0.0.0", "--port", "8000"]
