"""
Core configuration — loads from environment variables.
Copy .env.example to .env and fill in your values.
"""

from pydantic_settings import BaseSettings
from collections.abc import Iterable


class Settings(BaseSettings):

    # ── App ───────────────────────────────────────────────
    APP_NAME: str = "Homeopathy AI"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: Iterable[str] = ["http://localhost:3000"]

    # ── PostgreSQL ────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/homeopathy_ai"

    # ── Neo4j ─────────────────────────────────────────────
    NEO4J_URI:      str = "bolt://localhost:7687"
    NEO4J_USER:     str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # ── Redis (session cache) ─────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ── LLM ──────────────────────────────────────────────
    LLM_PROVIDER:   str = "anthropic"          # anthropic | openai | openrouter | mistral
    LLM_MODEL:      str = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS: int = 1000
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY:    str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_HTTP_REFERER: str = "http://localhost:8000"
    OPENROUTER_APP_TITLE: str = "Homeopathy AI DSS"

    # ── Embeddings ────────────────────────────────────────
    EMBEDDING_MODEL:  str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM:    int = 384

    # ── Repertory ─────────────────────────────────────────
    MIN_RUBRICS_FOR_ANALYSIS: int = 4
    MAX_CANDIDATE_REMEDIES:   int = 10
    TOP_REMEDIES_RETURNED:    int = 5

    # ── Ranking weights ───────────────────────────────────
    WEIGHT_REPERTORY: float = 0.50
    WEIGHT_RAG:       float = 0.30
    WEIGHT_OUTCOME:   float = 0.20

    class Config:
        env_file = ".env"


settings = Settings()
