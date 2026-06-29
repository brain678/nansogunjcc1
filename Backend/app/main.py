# app/main.py

"""
Main FastAPI application entry point for NANS Backend
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.common.exceptions import AppException
from app.presentation.api.v1.routers.auth import routes as auth_routes
from app.presentation.api.v1.routers.documents import router as documents_router
from app.presentation.api.v1.routers.identity import router as identity_router, qr_router
from app.presentation.api.v1.routers.members import router as members_router
from app.presentation.api.v1.routers.meetings import router as meetings_router
from app.presentation.api.v1.routers.users import router as users_router
from app.core.database import connect_to_db, disconnect_from_db
from app.core.config import PROJECT_ROOT, settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting NANS Backend Application")
    logger.info(f"📋 DEBUG: MONGODB_URL = {settings.MONGODB_URL}")
    logger.info(f"📋 DEBUG: DATABASE_NAME = {settings.DATABASE_NAME}")
    
    # Initialize database connection
    db_connected = await connect_to_db()
    
    if db_connected:
        logger.info("=" * 60)
        logger.info("🚀 NANS Backend API is ready!")
        logger.info("=" * 60)
    else:
        logger.warning("⚠️  Running without database connection")
    
    yield
    
    # Shutdown
    logger.info("Shutting down NANS Backend Application")
    await disconnect_from_db()


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="NANS Backend API",
        description="National Association of Nigerian Students (NANS) Backend API",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # ============= MIDDLEWARE =============
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )
    
    # ============= EXCEPTION HANDLERS =============
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):
        """Handle application exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "code": exc.code,
                    "status_code": exc.status_code
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "Internal server error",
                    "code": "INTERNAL_SERVER_ERROR",
                    "status_code": 500
                }
            }
        )
    
    # ============= ROUTES =============
    
    upload_dir = PROJECT_ROOT / settings.UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")
    
    # Health check endpoint
    @app.get(
        "/health",
        tags=["health"],
        summary="Health check",
        description="Check if the API is running"
    )
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": "1.0.0"
        }
    
    # API v1 routes
    app.include_router(auth_routes.router)
    app.include_router(documents_router)
    app.include_router(members_router)
    app.include_router(meetings_router)
    app.include_router(users_router)
    app.include_router(identity_router)
    app.include_router(qr_router)
    
    logger.info("FastAPI application configured successfully")
    return app


# Create app instance
app = create_app()


# Allow running with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
