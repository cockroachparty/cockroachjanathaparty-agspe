"""
AGSPE Backend - FastAPI Application Entry Point
Adani Group Strategic Prediction Engine API Server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .config import settings
from .api.routes import router

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    AGSPE - Adani Group Strategic Prediction Engine API

    An automated intelligence platform that ingests public data regarding
    the Adani Group, validates information through a multi-tier cross-source
    protocol, and generates probabilistic predictions on future business moves.

    **Repository:** https://github.com/cockroachparty/cockroachjanathaparty-agspe

    **Disclaimer:** For informational purposes only. Not financial or investment advice.
    Data based on publicly available records.
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print(f"[AGSPE] Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"[AGSPE] Debug mode: {settings.DEBUG}")
    print(f"[AGSPE] CORS origins: {settings.CORS_ORIGINS}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "repository": settings.APP_REPO,
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/health",
        "disclaimer": "For informational purposes only. Not financial or investment advice. Data based on publicly available records.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
