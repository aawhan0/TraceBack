from datetime import datetime, timezone

from app.observability.audit import AuditEvent
from app.repository.audit import SQLiteAuditStore


def event(index: int) -> AuditEvent:
    return AuditEvent(
        event_id=f"event-{index}",
        event_type="investigation.completed",
        occurred_at=datetime(2026, 1, index, tzinfo=timezone.utc),
        actor="system",
        resource_type="run",
        resource_id=f"run-{index}",
        payload={"passed": True, "index": index},
    )


def test_audit_store_round_trips_events(tmp_path) -> None:
    store = SQLiteAuditStore(str(tmp_path / "audit.db"))
    store.append(event(1))
    assert store.list(resource_type="run") == [event(1)]


def test_audit_store_filters_and_limits(tmp_path) -> None:
    store = SQLiteAuditStore(str(tmp_path / "audit.db"))
    for index in range(1, 4):
        store.append(event(index))
    assert [item.event_id for item in store.list(limit=2)] == ["event-3", "event-2"]
    assert store.list(resource_id="missing") == []


def test_audit_store_rejects_bad_limit(tmp_path) -> None:
    store = SQLiteAuditStore(str(tmp_path / "audit.db"))
    try:
        store.list(limit=0)
    except ValueError as exc:
        assert "between 1 and 1000" in str(exc)
    else:
        raise AssertionError("expected ValueError")
