# ToolGuard — AI application security layer
# Build: docker build -t toolguard .
# Run:   docker run -p 8400:8400 toolguard

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --upgrade pip && \
    pip install -e .

# Copy configuration.
COPY config/ ./config/

EXPOSE 8400

CMD ["uvicorn", "toolguard.main:app", "--host", "0.0.0.0", "--port", "8400"]
