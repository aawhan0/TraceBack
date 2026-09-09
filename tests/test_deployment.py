from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_container_definition_exists_and_runs_as_non_root() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "FROM python:3.12-slim" in dockerfile
    assert "USER traceback" in dockerfile
    assert 'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]' in dockerfile


def test_container_persists_database_outside_application_image() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "TRACEBACK_DATABASE_PATH=/data/traceback.db" in dockerfile
    assert "mkdir -p /data" in dockerfile
    assert "chown -R traceback:traceback /app /data" in dockerfile


def test_dockerignore_excludes_local_runtime_state() -> None:
    dockerignore = (ROOT / ".dockerignore").read_text()
    assert "data/" in dockerignore
    assert "*.db" in dockerignore
    assert ".git" in dockerignore
