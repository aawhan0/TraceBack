from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from time import perf_counter
from typing import Callable
from uuid import uuid4

from app.repository.runs import utc_now


@dataclass(frozen=True)
class TraceEvent:
    """A structured event emitted by an investigation workflow."""

    event_id: str
    name: str
    timestamp: datetime
    trace_id: str
    attributes: dict[str, str] = field(default_factory=dict)


class EventSink:
    """Small dependency-free event sink suitable for tests and local services."""

    def emit(self, event: TraceEvent) -> None:
        raise NotImplementedError


class InMemoryEventSink(EventSink):
    """Thread-safe event collector used by tests and development."""

    def __init__(self) -> None:
        self._events: list[TraceEvent] = []
        self._lock = Lock()

    def emit(self, event: TraceEvent) -> None:
        with self._lock:
            self._events.append(event)

    def events(self, trace_id: str | None = None) -> tuple[TraceEvent, ...]:
        with self._lock:
            events = tuple(self._events)
        if trace_id is None:
            return events
        return tuple(event for event in events if event.trace_id == trace_id)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


class NullEventSink(EventSink):
    """Default sink that preserves zero-cost behavior when tracing is unused."""

    def emit(self, event: TraceEvent) -> None:
        return None


@dataclass(frozen=True)
class TraceContext:
    trace_id: str
    sink: EventSink

    @classmethod
    def create(cls, sink: EventSink | None = None) -> "TraceContext":
        return cls(trace_id=str(uuid4()), sink=sink or NullEventSink())

    def record(self, name: str, **attributes: object) -> TraceEvent:
        event = TraceEvent(
            event_id=str(uuid4()),
            name=name,
            timestamp=utc_now(),
            trace_id=self.trace_id,
            attributes={key: str(value) for key, value in attributes.items()},
        )
        self.sink.emit(event)
        return event


@dataclass(frozen=True)
class SpanResult:
    name: str
    duration_ms: float
    trace_id: str


class TraceSpan:
    """Context manager that records start, completion and failure events."""

    def __init__(self, context: TraceContext, name: str, **attributes: object) -> None:
        self.context = context
        self.name = name
        self.attributes = attributes
        self._started = 0.0

    def __enter__(self) -> "TraceSpan":
        self._started = perf_counter()
        self.context.record(f"{self.name}.started", **self.attributes)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        duration_ms = (perf_counter() - self._started) * 1000
        if exc_type is None:
            self.context.record(
                f"{self.name}.completed",
                duration_ms=f"{duration_ms:.3f}",
                **self.attributes,
            )
        else:
            self.context.record(
                f"{self.name}.failed",
                duration_ms=f"{duration_ms:.3f}",
                error=exc_type.__name__,
                **self.attributes,
            )
        return False

    def result(self) -> SpanResult:
        if self._started == 0:
            raise RuntimeError("span has not started")
        return SpanResult(
            name=self.name,
            duration_ms=(perf_counter() - self._started) * 1000,
            trace_id=self.context.trace_id,
        )


def instrument(
    context: TraceContext,
    name: str,
    operation: Callable[[], object],
    **attributes: object,
) -> object:
    """Execute an operation inside a trace span."""
    with TraceSpan(context, name, **attributes):
        return operation()
