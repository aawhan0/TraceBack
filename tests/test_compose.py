from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_compose_defines_persistent_api_service() -> None:
    compose = (ROOT / "compose.yaml").read_text()
    assert "services:" in compose
    assert "traceback:" in compose
    assert 'build:' in compose
    assert "traceback-data:/data" in compose
    assert '8000:8000' in compose
    assert "restart: unless-stopped" in compose


def test_compose_keeps_database_path_inside_persistent_volume() -> None:
    compose = (ROOT / "compose.yaml").read_text()
    assert "TRACEBACK_DATABASE_PATH: /data/traceback.db" in compose
    assert "traceback-data:" in compose
    assert "init: true" in compose
