"""
HPES FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import upload, extract, feedback, export as export_route
from app.routes import sessions, text_input  # v2.0 routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("Initializing database...")
    init_db()
    print("HPES Backend started")
    yield
    # Shutdown
    print("HPES Backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="HPES API",
    description="Hybrid-Professional Extraction System API",
    version="2.0.0",  # Updated to v2.0
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1.0 routers
app.include_router(upload.router)
app.include_router(extract.router)
app.include_router(feedback.router)
app.include_router(export_route.router)

# Include v2.0 routers
app.include_router(sessions.router)
app.include_router(text_input.router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "HPES API v2.0",
        "version": "2.0.0",
        "docs": "/docs",
        "features": ["sessions", "text-input", "batch-processing"]
    }


@app.get("/health")
def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy"}
