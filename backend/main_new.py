"""
AI Wireframing Tool - Production Backend
A lean, modular FastAPI application for intelligent wireframe generation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings, ensure_directories
from app.utils.logging import setup_logging
from app.api.routes import router


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    # Setup logging
    setup_logging()
    
    # Ensure required directories exist
    ensure_directories()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Intelligent wireframe generation from natural language prompts",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router)
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main_new:app",
        host=settings.api_host,
        port=8000, 
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
