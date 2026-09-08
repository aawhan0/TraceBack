import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model: str = "llama3.2"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_timeout: float = 60.0
    database_path: str = "data/traceback.db"

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            model=os.getenv("TRACEBACK_MODEL", "llama3.2"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
            ollama_timeout=float(os.getenv("TRACEBACK_OLLAMA_TIMEOUT", "60")),
            database_path=os.getenv("TRACEBACK_DATABASE_PATH", "data/traceback.db"),
        )
