"""
HPES FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.database import init_db
from app.routes import upload, extract, feedback, export as export_route
from app.routes import sessions, text_input, batch, analytics, search, git, system  # v2.0 routes


# Setup Jinja2 templates
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)


from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.middleware.security import SecurityHeadersMiddleware

# ...

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

# Global Exception Handler (Mask 500 Errors)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error (real world: use proper logger)
    print(f"CRITICAL ERROR: {str(exc)}")
    # Return generic message to user
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

# Security Middleware
app.add_middleware(SecurityHeadersMiddleware)

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     print(f"DEBUG MIDDLEWARE: Request {request.method} {request.url.path}")
#     response = await call_next(request)
#     print(f"DEBUG MIDDLEWARE: Response {response.status_code}")
#     return response

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
app.include_router(batch.router)
app.include_router(analytics.router)
app.include_router(search.router)
app.include_router(git.router)
app.include_router(system.router)


@app.get("/")
def root(request: Request):
    """Root endpoint - Serve beautiful bilingual landing page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy"}


@app.get("/api-guide")
def api_guide():
    """Serve API Guide markdown file."""
    guide_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "API_GUIDE.md")
    return FileResponse(
        guide_path,
        media_type="text/markdown",
        filename="API_GUIDE.md"
    )
