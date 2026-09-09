from app.evaluation.provenance import BenchmarkProvenance


def test_provenance_reads_ci_revision(monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_GIT_SHA", "abc123")
    monkeypatch.setenv("TRACEBACK_ENVIRONMENT", "test")

    provenance = BenchmarkProvenance.from_environment(
        provider="ollama",
        model="llama3.2",
    )

    assert provenance.git_revision == "abc123"
    assert provenance.environment == "test"
    assert provenance.provider == "ollama"
    assert provenance.model == "llama3.2"
    assert provenance.python_version


def test_provenance_prefers_traceback_revision(monkeypatch) -> None:
    monkeypatch.setenv("TRACEBACK_GIT_SHA", "traceback-sha")
    monkeypatch.setenv("GITHUB_SHA", "github-sha")

    provenance = BenchmarkProvenance.from_environment()

    assert provenance.git_revision == "traceback-sha"


def test_provenance_falls_back_when_revision_is_unavailable(monkeypatch) -> None:
    monkeypatch.delenv("TRACEBACK_GIT_SHA", raising=False)
    monkeypatch.delenv("GITHUB_SHA", raising=False)

    provenance = BenchmarkProvenance.from_environment()

    assert provenance.git_revision == "unknown"
