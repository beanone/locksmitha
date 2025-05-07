FROM python:3.11-slim

LABEL maintainer="Beanone Team <beanone@example.com>"
LABEL description="Locksmitha Authentication Service"
LABEL version="1.0.0"

WORKDIR /app

# Copy only requirements first to leverage cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Then copy application code
COPY src/ src/

# Add non-root user
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["uvicorn", "src.locksmitha.main:app", "--host", "0.0.0.0", "--port", "8001"]
