"""
Example data models for the API
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str

class APIInfo(BaseModel):
    """API info response model"""
    name: str
    version: str
    environment: str
    framework: str
