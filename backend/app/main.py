from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import engine
from app.models import product, machine_state, defect
from app.api.endpoints import analytics

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Krevera Analytics API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    yield
    logger.info("Shutting down Krevera Analytics API...")
    engine.dispose()


app = FastAPI(
    title="Krevera Manufacturing Analytics API",
    description="API for manufacturing quality analytics and defect tracking",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "krevera-analytics-api",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    return {
        "message": "Krevera Manufacturing Analytics API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "analytics": "/api/v1/analytics",
        }
    }


app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database error occurred",
            "error": str(exc) if settings.ENVIRONMENT == "development" else "Internal server error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info",
    )