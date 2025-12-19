from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config.database import Base, engine
from app.config.deps import get_db
from app.config.logging_config import setup_logging
from app.core.events import startup_event, shutdown_event
from app.core.exception_handlers import register_exception_handlers
from app.middleware.cors_middleware import setup_cors
from app.middleware.logging_middleware import log_requests_middleware
from app.routes import auth, category

# ===============================
# Setup Logging
# ===============================
setup_logging()

# ===============================
# Create Database Tables
# ===============================
Base.metadata.create_all(bind=engine)


# ===============================
# Application Lifespan Events
# ===============================
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    startup_event()
    yield
    # Shutdown
    shutdown_event()


# ===============================
# Initialize FastAPI Application
# ===============================
app = FastAPI(
    title="ASMI Dashboard API",
    description="Backend API untuk ASMI Dashboard menggunakan FastAPI dan PostgreSQL",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ===============================
# Register Exception Handlers
# ===============================
register_exception_handlers(app)

# ===============================
# Setup Middleware
# ===============================
# Logging middleware (harus di atas CORS)
app.middleware("http")(log_requests_middleware)

# CORS middleware
setup_cors(app)

# ===============================
# Include Routers
# ===============================
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(category.router, prefix="/api/categories", tags=["Categories"])

# ===============================
# Health Check Endpoints
# ===============================
@app.get("/", tags=["Health"])
def root():
    """Root endpoint - API info"""
    return {
        "app": "ASMI Dashboard API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/health/db", tags=["Health"])
def database_health_check(db: Session = Depends(get_db)):
    """Database health check endpoint"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "database": "postgresql",
            "status": "connected",
            "host": engine.url.host,
            "database": engine.url.database
        }
    except Exception as e:
        return {
            "database": "postgresql",
            "status": "disconnected",
            "error": str(e)
        }
