"""Health check routes."""

from datetime import datetime, timezone

from fastapi import APIRouter

from ..config.settings import settings

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'version': settings.app_version
    }

@router.get("/info")
async def info():
    """API info endpoint"""
    return {
        'name': settings.app_name,
        'version': settings.app_version,
        'environment': settings.environment,
        'framework': 'FastAPI'
    }
