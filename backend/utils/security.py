"""
Security helpers for authentication, token handling, and rate limiting.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request


CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_text(value: Optional[str], max_length: int = 1000) -> str:
    if value is None:
        return ""

    normalized = CONTROL_CHAR_PATTERN.sub("", value).strip()
    if len(normalized) > max_length:
        normalized = normalized[:max_length]
    return normalized


def sanitize_dict(value: Any, max_length: int = 1000) -> Any:
    if isinstance(value, str):
        return sanitize_text(value, max_length=max_length)
    if isinstance(value, list):
        return [sanitize_dict(item, max_length=max_length) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_dict(item, max_length=max_length) for key, item in value.items()}
    return value


def _base64url_encode(raw_bytes: bytes) -> str:
    return base64.urlsafe_b64encode(raw_bytes).decode("utf-8").rstrip("=")


def _base64url_decode(encoded: str) -> bytes:
    padding = "=" * (-len(encoded) % 4)
    return base64.urlsafe_b64decode(encoded + padding)


def create_session_token(payload: Dict[str, Any], secret: str, expires_in_seconds: int = 86400) -> str:
    issued_at = int(time.time())
    token_payload = dict(payload)
    token_payload["iat"] = issued_at
    token_payload["exp"] = issued_at + expires_in_seconds

    payload_bytes = json.dumps(token_payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
    return f"{_base64url_encode(payload_bytes)}.{_base64url_encode(signature)}"


def verify_session_token(token: str, secret: str) -> Optional[Dict[str, Any]]:
    try:
        payload_part, signature_part = token.split(".", 1)
        payload_bytes = _base64url_decode(payload_part)
        provided_signature = _base64url_decode(signature_part)

        expected_signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_signature, provided_signature):
            return None

        payload = json.loads(payload_bytes.decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after_seconds: int = 0


class RateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._requests: dict[str, list[float]] = {}

    def check(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        now = time.time()
        with self._lock:
            timestamps = [ts for ts in self._requests.get(key, []) if now - ts < window_seconds]
            allowed = len(timestamps) < limit
            retry_after = 0
            if not allowed and timestamps:
                retry_after = max(1, int(window_seconds - (now - timestamps[0])))
            if allowed:
                timestamps.append(now)
            self._requests[key] = timestamps
        return RateLimitResult(allowed=allowed, retry_after_seconds=retry_after)


rate_limiter = RateLimiter()


def verify_google_id_token(id_token: str, client_id: Optional[str]) -> Dict[str, Any]:
    if not client_id:
        raise ValueError("GOOGLE_CLIENT_ID is not configured")

    url = "https://oauth2.googleapis.com/tokeninfo?" + urllib_parse.urlencode({"id_token": id_token})
    try:
        with urllib_request.urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib_error.HTTPError as exc:
        raise ValueError("Invalid Google ID token") from exc
    except Exception as exc:
        raise ValueError("Unable to verify Google ID token") from exc

    if payload.get("aud") != client_id:
        raise ValueError("Google ID token audience mismatch")

    if payload.get("email_verified") not in {True, "true", "True"}:
        raise ValueError("Google account email is not verified")

    return {
        "sub": payload.get("sub", ""),
        "email": payload.get("email", ""),
        "name": payload.get("name") or payload.get("email", ""),
        "picture": payload.get("picture"),
        "provider": "google",
    }
