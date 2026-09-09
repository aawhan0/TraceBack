from app.config import Settings


def get_settings() -> Settings:
    return Settings.from_environment()


def reset_settings_cache() -> None:
    """Compatibility hook for tests and future cached dependency implementations."""
    return None
