FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    DEBUG=false \
    DATABASE_URL=sqlite+aiosqlite:///./data/homeopathy_ai.db

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos "" appuser

COPY requirements.deploy.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.deploy.txt

COPY . .

RUN mkdir -p /app/data && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
