"""SecureAnswer backend application entrypoint."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routes (relative imports for package structure)
from .config.settings import settings
from .routes.auth import router as auth_router
from .routes.health import router as health_router
from .routes.rag import router as rag_router
from .routes.integration import router as integration_router

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Enterprise question-answering platform API",
    version=settings.app_version,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

@app.middleware("http")
async def enforce_request_limits(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            payload_size = int(content_length)
        except ValueError:
            return JSONResponse({"detail": "Invalid Content-Length header"}, status_code=400)

        path = request.url.path
        if path.startswith("/api/auth/") and payload_size > 16 * 1024:
            return JSONResponse({"detail": "Authentication payload too large"}, status_code=413)

        if path == "/api/ingestion/upload":
            max_upload_bytes = settings.max_upload_mb * 1024 * 1024
            if payload_size > max_upload_bytes:
                return JSONResponse({"detail": "Upload payload too large"}, status_code=413)

        if path.startswith("/api/") and payload_size > settings.max_request_body_bytes:
            return JSONResponse({"detail": "Request payload too large"}, status_code=413)

    return await call_next(request)

# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(rag_router)
app.include_router(integration_router)

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse({
        'message': 'Welcome to SecureAnswer API',
        'docs': '/docs',
        'health': '/api/health'
    }, status_code=200)

# ============================================================================
# LIFESPAN EVENTS (Optional: for startup/shutdown logic)
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    print(f"Backend started in {settings.environment} mode")
    print(f"API Docs: http://localhost:{settings.port}/docs")
    if settings.environment.lower() == "production" and not settings.auth_secret_key:
        print("Warning: AUTH_SECRET_KEY is not configured. Production auth tokens will fail.")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    print("🛑 Backend shutdown")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
