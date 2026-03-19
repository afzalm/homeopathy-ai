"""
Homeopathy AI Decision Support System
FastAPI Application Entry Point
Version: 1.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

from core.config import settings
from core.database import init_db
from api.session_routes import router as session_router
from api.chat_routes import router as chat_router
from api.remedy_routes import router as remedy_router
from api.case_routes import router as case_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Homeopathy AI API...")
    await init_db()
    logger.info("Database initialised")
    yield
    logger.info("Shutting down Homeopathy AI API...")


app = FastAPI(
    title="Homeopathy AI Decision Support System",
    description="AI-powered homeopathic case analysis and remedy recommendation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────
app.include_router(session_router, prefix="/api/v1/sessions",  tags=["Sessions"])
app.include_router(chat_router,    prefix="/api/v1/chat",      tags=["Chat"])
app.include_router(remedy_router,  prefix="/api/v1/remedies",  tags=["Remedies"])
app.include_router(case_router,    prefix="/api/v1/cases",     tags=["Cases"])


# ── Static Files ──────────────────────────────────────────
@app.get("/chat", tags=["Chat UI"])
async def chat_ui():
    """Serve the chat interface."""
    chat_path = os.path.join(os.path.dirname(__file__), "static", "chat.html")
    return FileResponse(chat_path)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Homeopathy AI Decision Support System",
        "version": "1.0.0",
        "description": "AI-powered homeopathic case analysis and remedy recommendation",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "sessions": "/api/v1/sessions",
            "chat": "/api/v1/chat",
            "remedies": "/api/v1/remedies",
            "cases": "/api/v1/cases"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
