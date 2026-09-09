from fastapi.testclient import TestClient

from app.evaluation.experiments import ExperimentResult
from app.evaluation.health import quality_snapshot, weighted_pass_rate
from app.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "traceback"}



def _result(rate: float) -> ExperimentResult:
    return ExperimentResult("smoke", 10, int(rate * 10), rate, 0.8, 100, {"db": rate})


def test_quality_snapshot_marks_healthy_result() -> None:
    snapshot = quality_snapshot(_result(1.0))
    assert snapshot.healthy
    assert snapshot.total_runs == 10
    assert snapshot.pass_rate == 1.0
    assert snapshot.pass_rate_lower_bound < 1.0


def test_quality_snapshot_respects_threshold() -> None:
    snapshot = quality_snapshot(_result(0.8), minimum_pass_rate=0.9)
    assert not snapshot.healthy


def test_quality_snapshot_validates_threshold() -> None:
    try:
        quality_snapshot(_result(1.0), minimum_pass_rate=2)
    except ValueError as exc:
        assert "between" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_weighted_pass_rate() -> None:
    assert weighted_pass_rate([(True, 3), (False, 1)]) == 0.75


def test_weighted_pass_rate_rejects_empty_and_zero_weight() -> None:
    for values in ([], [(True, 0)]):
        try:
            weighted_pass_rate(values)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")
