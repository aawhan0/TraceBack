import pytest

from app.api.security import RateLimiter
from app.services.request_validation import (
    validate_database_path,
    validate_http_url,
    validate_request_id,
)


def test_rate_limiter_allows_requests_until_limit() -> None:
    limiter = RateLimiter(max_requests=2, window_seconds=60)
    assert limiter.allow("client") is True
    assert limiter.allow("client") is True
    assert limiter.allow("client") is False


def test_rate_limiter_isolated_by_client() -> None:
    limiter = RateLimiter(max_requests=1, window_seconds=60)
    assert limiter.allow("one") is True
    assert limiter.allow("two") is True


def test_rate_limiter_reset_clears_state() -> None:
    limiter = RateLimiter(max_requests=1)
    assert limiter.allow("client") is True
    limiter.reset()
    assert limiter.allow("client") is True


def test_rate_limiter_rejects_invalid_configuration() -> None:
    with pytest.raises(ValueError):
        RateLimiter(max_requests=0)
    with pytest.raises(ValueError):
        RateLimiter(window_seconds=0)


def test_request_validation_rejects_bad_values() -> None:
    with pytest.raises(ValueError):
        validate_request_id("")
    with pytest.raises(ValueError):
        validate_request_id("x\x00")
    with pytest.raises(ValueError):
        validate_http_url("ftp://example.com")
    with pytest.raises(ValueError):
        validate_database_path("")


def test_request_validation_accepts_normal_values() -> None:
    assert validate_request_id("req-123") == "req-123"
    assert validate_http_url("https://example.com/") == "https://example.com"
    assert validate_database_path(" data/app.db ") == "data/app.db"
