"""
Authentication routes for SecureAnswer.
"""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from ..config.settings import settings
from ..utils.security import create_session_token, rate_limiter, sanitize_text, verify_google_id_token, verify_session_token

try:
    from supabase_client import SupabaseDB
except Exception:  # pragma: no cover - optional dependency path
    SupabaseDB = None


router = APIRouter(prefix="/api/auth", tags=["auth"])


class DevLoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., min_length=32, max_length=4096)


class TestLoginRequest(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    email: str | None = Field(default=None, max_length=254)


def _rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"{client_host}:{request.url.path}"
    result = rate_limiter.check(
        key=key,
        limit=settings.auth_rate_limit_max_attempts,
        window_seconds=settings.auth_rate_limit_window_seconds,
    )
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please try again later.",
            headers={"Retry-After": str(result.retry_after_seconds)},
        )


async def _store_user(email: str, name: str, provider: str) -> None:
    if SupabaseDB is None:
        return

    try:
        db = SupabaseDB()
        await db.get_or_create_user(email=email, name=name, role="user")
        await db.log_action(user_id=email, action_type=f"auth:{provider}", metadata={"provider": provider})
    except Exception:
        return


def _issue_token(user: dict[str, str]) -> dict[str, object]:
    token = create_session_token(user, settings.auth_secret_key)
    return {"token": token, "user": user}


def _is_testing_login_enabled() -> bool:
    return settings.environment != "production" and settings.enable_test_login


def _read_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return authorization.removeprefix("Bearer ").strip()


@router.post("/login")
async def dev_login(request: Request, payload: DevLoginRequest):
    _rate_limit(request)

    if settings.environment == "production" and not settings.enable_dev_login:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Password login is disabled in production")

    if not settings.auth_dev_email or not settings.auth_dev_password:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Developer login is not configured")

    email = sanitize_text(payload.email, max_length=254).lower()
    password = sanitize_text(payload.password, max_length=128)

    if email != settings.auth_dev_email.lower() or password != settings.auth_dev_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = {
        "id": email,
        "email": email,
        "name": email.split("@")[0],
        "provider": "password",
    }
    await _store_user(email=email, name=user["name"], provider="password")
    return _issue_token(user)


@router.post("/test-login")
async def test_login(request: Request, payload: TestLoginRequest | None = None):
    _rate_limit(request)

    if not _is_testing_login_enabled():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Test login is disabled in production")

    payload = payload or TestLoginRequest()
    base_email = sanitize_text(payload.email or "test.user@secureanswer.local", max_length=254).lower()
    email = base_email if "@" in base_email else "test.user@secureanswer.local"
    name = sanitize_text(payload.name or "Test User", max_length=120)

    user = {
        "id": email,
        "email": email,
        "name": name,
        "provider": "test",
    }
    await _store_user(email=email, name=name, provider="test")
    return _issue_token(user)


@router.post("/google")
async def google_login(request: Request, payload: GoogleLoginRequest):
    _rate_limit(request)

    user_info = verify_google_id_token(payload.id_token, settings.google_client_id)
    email = sanitize_text(user_info["email"], max_length=254).lower()
    name = sanitize_text(user_info.get("name") or email, max_length=120)
    user = {
        "id": user_info.get("sub") or email,
        "email": email,
        "name": name,
        "provider": "google",
    }
    await _store_user(email=email, name=name, provider="google")
    return _issue_token(user)


@router.get("/me")
async def current_user(authorization: str | None = Header(default=None)):
    token = _read_bearer_token(authorization)
    payload = verify_session_token(token, settings.auth_secret_key)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return {"user": payload}


@router.post("/logout")
async def logout():
    return {"status": "ok"}
