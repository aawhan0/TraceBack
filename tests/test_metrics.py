from app.observability.metrics import MetricsRegistry


def test_metrics_count_and_observe() -> None:
    metrics = MetricsRegistry()
    metrics.increment("investigations.total")
    metrics.increment("investigations.total", 2)
    metrics.observe("investigation.duration", 0.25)
    snapshot = metrics.snapshot()
    assert snapshot.counters["investigations.total"] == 3
    assert snapshot.timings["investigation.duration"][0] == 1


def test_metrics_timer_records_duration() -> None:
    metrics = MetricsRegistry()
    with metrics.time("request.duration"):
        pass
    assert metrics.snapshot().timings["request.duration"][0] == 1


def test_metrics_reject_invalid_values() -> None:
    metrics = MetricsRegistry()
    try:
        metrics.increment("")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
