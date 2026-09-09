import logging

from app.observability.events import InMemoryEventSink, TraceContext, TraceSpan, instrument
from app.observability.logging import JsonFormatter, LogContext, configure_logging, logger_for_trace


def test_trace_context_records_events() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    event = context.record("investigation.started", scenario_id="db", attempt=1)
    assert event.trace_id == context.trace_id
    assert event.attributes == {"scenario_id": "db", "attempt": "1"}
    assert sink.events(context.trace_id) == (event,)


def test_trace_span_records_completion() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    with TraceSpan(context, "work", scenario_id="db"):
        pass
    names = [event.name for event in sink.events(context.trace_id)]
    assert names == ["work.started", "work.completed"]


def test_trace_span_records_failure_without_swallowing() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    try:
        with TraceSpan(context, "work"):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    names = [event.name for event in sink.events(context.trace_id)]
    assert names == ["work.started", "work.failed"]
    assert sink.events(context.trace_id)[1].attributes["error"] == "RuntimeError"


def test_trace_span_result_requires_started_span() -> None:
    context = TraceContext.create()
    span = TraceSpan(context, "work")
    try:
        span.result()
    except RuntimeError as exc:
        assert "not started" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")


def test_instrument_executes_operation_and_returns_result() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    result = instrument(context, "calculation", lambda: 42, value=3)
    assert result == 42
    assert [event.name for event in sink.events()] == [
        "calculation.started",
        "calculation.completed",
    ]


def test_in_memory_sink_can_clear() -> None:
    sink = InMemoryEventSink()
    context = TraceContext.create(sink)
    context.record("event")
    sink.clear()
    assert sink.events() == ()


def test_json_formatter_emits_structured_fields() -> None:
    formatter = JsonFormatter(LogContext(environment="test"))
    record = logging.LogRecord("traceback", logging.INFO, __file__, 1, "hello %s", ("world",), None)
    record.trace_id = "trace-1"
    record.scenario_id = "db"
    output = formatter.format(record)
    assert '"environment": "test"' in output
    assert '"trace_id": "trace-1"' in output
    assert '"scenario_id": "db"' in output


def test_configure_logging_does_not_duplicate_json_handlers() -> None:
    logger = logging.getLogger()
    original = list(logger.handlers)
    try:
        logger.handlers.clear()
        configure_logging()
        configure_logging()
        assert sum(isinstance(handler.formatter, JsonFormatter) for handler in logger.handlers) == 1
    finally:
        logger.handlers[:] = original


def test_trace_logger_adapter_adds_trace_id() -> None:
    adapter = logger_for_trace("traceback.test", "trace-123")
    message, kwargs = adapter.process("hello", {})
    assert message == "hello"
    assert kwargs["extra"]["trace_id"] == "trace-123"
