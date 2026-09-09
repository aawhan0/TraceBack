from __future__ import annotations

from urllib.parse import urlparse


def validate_database_path(path: str) -> str:
    if not path or not path.strip():
        raise ValueError("database path cannot be empty")
    if "\x00" in path:
        raise ValueError("database path contains a null byte")
    return path.strip()


def validate_request_id(value: str) -> str:
    value = value.strip()
    if not value or len(value) > 128:
        raise ValueError("request ID must contain 1-128 characters")
    if any(ord(char) < 32 for char in value):
        raise ValueError("request ID contains control characters")
    return value


def validate_http_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must use HTTP or HTTPS")
    return value.rstrip("/")
