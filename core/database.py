"""
Async database connection via SQLAlchemy + aiosqlite.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# SQLite doesn't support pool_size/max_overflow, only use for PostgreSQL
engine_kwargs = {}
if "sqlite" not in settings.DATABASE_URL:
    engine_kwargs = {"pool_size": 10, "max_overflow": 20}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        # Import all models so Base knows about them
        from database import models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created")


async def get_db():
    """FastAPI dependency — yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
