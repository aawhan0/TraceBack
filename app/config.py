import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Settings:
    model: str = "llama3.2"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_timeout: float = 60.0
    database_path: str = "data/traceback.db"
    cors_origins: tuple[str, ...] = ()
    environment: str = "development"
    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"
    rate_limit_requests: int = 120
    rate_limit_window_seconds: float = 60.0

    @classmethod
    def from_environment(cls) -> "Settings":
        origins = tuple(
            item.strip()
            for item in os.getenv("TRACEBACK_CORS_ORIGINS", "").split(",")
            if item.strip()
        )
        settings = cls(
            model=os.getenv("TRACEBACK_MODEL", "llama3.2").strip(),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/"),
            ollama_timeout=float(os.getenv("TRACEBACK_OLLAMA_TIMEOUT", "60")),
            database_path=os.getenv("TRACEBACK_DATABASE_PATH", "data/traceback.db"),
            cors_origins=origins,
            environment=os.getenv("TRACEBACK_ENVIRONMENT", "development").strip().lower(),
            log_level=os.getenv("TRACEBACK_LOG_LEVEL", "INFO").strip().upper(),
            request_id_header=os.getenv("TRACEBACK_REQUEST_ID_HEADER", "X-Request-ID").strip(),
            rate_limit_requests=int(os.getenv("TRACEBACK_RATE_LIMIT_REQUESTS", "120")),
            rate_limit_window_seconds=float(os.getenv("TRACEBACK_RATE_LIMIT_WINDOW_SECONDS", "60")),
        )
        settings.validate()
        return settings

    def validate(self) -> None:
        if not self.model:
            raise ValueError("TRACEBACK_MODEL cannot be empty")
        if self.ollama_timeout <= 0:
            raise ValueError("TRACEBACK_OLLAMA_TIMEOUT must be positive")
        if self.environment not in {"development", "test", "production"}:
            raise ValueError("TRACEBACK_ENVIRONMENT must be development, test, or production")
        if self.log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("TRACEBACK_LOG_LEVEL is invalid")
        if self.rate_limit_requests <= 0:
            raise ValueError("TRACEBACK_RATE_LIMIT_REQUESTS must be positive")
        if self.rate_limit_window_seconds <= 0:
            raise ValueError("TRACEBACK_RATE_LIMIT_WINDOW_SECONDS must be positive")
        if not self.request_id_header:
            raise ValueError("TRACEBACK_REQUEST_ID_HEADER cannot be empty")
        parsed = urlparse(self.ollama_base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("OLLAMA_BASE_URL must be a valid HTTP(S) URL")
        if "*" in self.cors_origins and self.environment == "production":
            raise ValueError("wildcard CORS is not allowed in production")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"
