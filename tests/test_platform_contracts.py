import pytest

from app.evaluation.latency import LatencySample, percentile, summarize_latency
from app.observability.audit import AuditEvent, AuditLog
from app.observability.serialization import dumps
from app.providers.contracts import InvestigationContract, ProviderRegistry
from app.services.readiness import HealthCheck, ReadinessRegistry
from app.services.results import OperationResult, Status


def test_percentile_interpolates_values() -> None:
    assert percentile([10, 20, 30, 40], 50) == 25


def test_percentile_rejects_invalid_range() -> None:
    with pytest.raises(ValueError):
        percentile([1], 101)


def test_latency_summary_rejects_mixed_operations() -> None:
    samples = [LatencySample("a", 10), LatencySample("b", 20)]
    with pytest.raises(ValueError):
        summarize_latency(samples)


def test_latency_summary_has_distribution_metrics() -> None:
    summary = summarize_latency([LatencySample("investigate", value) for value in [10, 20, 30]])
    assert summary.count == 3
    assert summary.average_ms == 20
    assert summary.p50_ms == 20
    assert summary.p95_ms == 29


def test_audit_log_filters_and_orders_events() -> None:
    log = AuditLog()
    first = AuditEvent.create("created", actor="system", resource_type="run", resource_id="1")
    second = AuditEvent.create("evaluated", actor="system", resource_type="run", resource_id="1")
    log.append(first)
    log.append(second)
    assert [event.event_type for event in log.list(resource_id="1")] == ["evaluated", "created"]


def test_audit_event_validates_identity() -> None:
    with pytest.raises(ValueError):
        AuditEvent.create("", actor="system", resource_type="run", resource_id="1")


def test_provider_registry_is_explicit() -> None:
    class Fake:
        name = "fake"

    registry = ProviderRegistry()
    registry.register(Fake())
    assert registry.names() == ("fake",)
    assert registry.get("fake").name == "fake"


def test_provider_registry_rejects_duplicate() -> None:
    class Fake:
        name = "fake"

    registry = ProviderRegistry()
    registry.register(Fake())
    with pytest.raises(ValueError):
        registry.register(Fake())


def test_investigation_contract_contains_evidence() -> None:
    from app.scenarios.catalog import DATABASE_POOL_EXHAUSTION

    contract = InvestigationContract.for_scenario(DATABASE_POOL_EXHAUSTION)
    assert contract.scenario_id == DATABASE_POOL_EXHAUSTION.id
    assert DATABASE_POOL_EXHAUSTION.evidence[0].id in contract.user_prompt


def test_readiness_reports_failed_checks() -> None:
    registry = ReadinessRegistry()
    registry.set(HealthCheck("database", "ok", "reachable"))
    registry.set(HealthCheck("model", "failed", "unavailable"))
    report = registry.report()
    assert report.ready is False
    assert [item.name for item in report.failed] == ["model"]


def test_operation_result_measures_duration() -> None:
    result = OperationResult.success("investigation", {"passed": True})
    assert result.status is Status.SUCCESS
    assert result.duration_ms == 0
    assert result.data["passed"] is True


def test_serialization_is_stable() -> None:
    assert dumps({"b": 2, "a": 1}) == '{"a":1,"b":2}'
