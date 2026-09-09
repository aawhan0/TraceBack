import pytest

from app.config import Settings
from app.services.idempotency import IdempotencyStore


def test_settings_defaults_are_valid() -> None:
    settings = Settings()
    settings.validate()
    assert settings.environment == "development"


def test_settings_reject_invalid_environment() -> None:
    with pytest.raises(ValueError, match="TRACEBACK_ENVIRONMENT"):
        Settings(environment="staging").validate()


def test_settings_reject_wildcard_cors_in_production() -> None:
    with pytest.raises(ValueError, match="wildcard CORS"):
        Settings(environment="production", cors_origins=("*",)).validate()


def test_settings_reject_invalid_ollama_url() -> None:
    with pytest.raises(ValueError, match="OLLAMA_BASE_URL"):
        Settings(ollama_base_url="not-a-url").validate()


def test_idempotency_store_round_trips_values() -> None:
    store = IdempotencyStore[str]()
    assert store.get("run-1") is None
    store.put("run-1", "result")
    assert store.get("run-1") == "result"


def test_idempotency_store_replaces_existing_value() -> None:
    store = IdempotencyStore[str]()
    store.put("run-1", "first")
    store.put("run-1", "second")
    assert store.get("run-1") == "second"


def test_idempotency_requires_non_empty_key() -> None:
    store = IdempotencyStore[str]()
    with pytest.raises(ValueError):
        store.get("")


def test_idempotency_clear_removes_values() -> None:
    store = IdempotencyStore[str]()
    store.put("run-1", "result")
    store.clear()
    assert store.get("run-1") is None


def test_idempotency_rejects_invalid_limits() -> None:
    with pytest.raises(ValueError):
        IdempotencyStore[str](ttl_seconds=0)
    with pytest.raises(ValueError):
        IdempotencyStore[str](max_entries=0)

def test_settings_validate_rate_limit_configuration() -> None:
    with pytest.raises(ValueError, match="RATE_LIMIT_REQUESTS"):
        Settings(rate_limit_requests=0).validate()
    with pytest.raises(ValueError, match="RATE_LIMIT_WINDOW_SECONDS"):
        Settings(rate_limit_window_seconds=0).validate()
