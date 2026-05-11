"""Configuration settings for the backend application."""

import os
from typing import List, Optional

from dotenv import load_dotenv


load_dotenv()


def _csv_env(name: str, default: list[str]) -> list[str]:
    raw_value = os.getenv(name, "")
    if not raw_value.strip():
        return default
    return [item.strip() for item in raw_value.split(",") if item.strip()]


class Settings:
    """Application settings."""

    app_name: str = "SecureAnswer API"
    app_version: str = "1.0.0"
    environment: str = os.getenv("APP_ENV", os.getenv("FLASK_ENV", "development"))
    debug: bool = os.getenv("APP_ENV", os.getenv("FLASK_ENV", "development")) == "development"

    # Server
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))

    # CORS
    cors_origins: List[str] = _csv_env(
        "CORS_ORIGINS",
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "https://secure-answer.vercel.app",
        ],
    )

    # Request limits
    max_request_body_bytes: int = int(os.getenv("MAX_REQUEST_BODY_BYTES", "2000000"))
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "20"))

    # Auth
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    auth_secret_key: str = os.getenv("AUTH_SECRET_KEY", os.getenv("SECRET_KEY", "change-this-in-production"))
    auth_dev_email: Optional[str] = os.getenv("AUTH_DEV_EMAIL")
    auth_dev_password: Optional[str] = os.getenv("AUTH_DEV_PASSWORD")
    enable_test_login: bool = os.getenv("ENABLE_TEST_LOGIN", "true").lower() == "true"
    auth_rate_limit_window_seconds: int = int(os.getenv("AUTH_RATE_LIMIT_WINDOW_SECONDS", "900"))
    auth_rate_limit_max_attempts: int = int(os.getenv("AUTH_RATE_LIMIT_ATTEMPTS", "5"))
    enable_dev_login: bool = os.getenv("ENABLE_DEV_LOGIN", "false").lower() == "true"

settings = Settings()
