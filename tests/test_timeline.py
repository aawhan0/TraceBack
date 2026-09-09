from datetime import datetime, timedelta, timezone

from app.evaluation.timeline import build_timeline, render_timeline, total_duration
from app.observability.events import InMemoryEventSink, TraceContext, TraceSpan


def test_build_timeline_orders_events_and_reads_duration() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    with TraceSpan(context, "benchmark"):
        pass

    timeline = build_timeline(sink.events(context.trace_id))
    assert timeline.trace_id == context.trace_id
    assert timeline.event_count == 2
    assert timeline.names() == ("benchmark.started", "benchmark.completed")
    assert timeline.entries[1].duration_ms is not None


def test_timeline_filter_selects_event_prefix() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    context.record("benchmark.started")
    context.record("investigation.started")
    timeline = build_timeline(sink.events())
    selected = timeline.filter("benchmark")
    assert selected.names() == ("benchmark.started",)


def test_timeline_handles_empty_events() -> None:
    timeline = build_timeline([])
    assert timeline.trace_id == ""
    assert timeline.event_count == 0
    assert timeline.first_timestamp is None
    assert render_timeline(timeline) == "No trace events recorded.\n"


def test_timeline_render_contains_trace_and_event_names() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    context.record("benchmark.started")
    output = render_timeline(build_timeline(sink.events()))
    assert context.trace_id in output
    assert "benchmark.started" in output


def test_total_duration_ignores_events_without_duration() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    context.record("plain")
    timeline = build_timeline(sink.events())
    assert total_duration(timeline) == 0


def test_timeline_can_parse_explicit_duration() -> None:
    context = TraceContext.create(InMemoryEventSink())
    first = context.record("span.started")
    second = context.record("span.completed", duration_ms="12.5")
    assert second.timestamp >= first.timestamp
    timeline = build_timeline(context.sink.events())
    assert total_duration(timeline) == 12.5


def test_timeline_keeps_invalid_duration_non_fatal() -> None:
    context = TraceContext.create(InMemoryEventSink())
    context.record("span.completed", duration_ms="not-a-number")
    timeline = build_timeline(context.sink.events())
    assert timeline.entries[0].duration_ms is None
