from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.observability.events import TraceEvent


@dataclass(frozen=True)
class TimelineEntry:
    """Normalized trace event suitable for human-facing reports."""

    name: str
    timestamp: datetime
    duration_ms: float | None
    attributes: dict[str, str]


@dataclass(frozen=True)
class InvestigationTimeline:
    trace_id: str
    entries: tuple[TimelineEntry, ...]

    @property
    def event_count(self) -> int:
        return len(self.entries)

    @property
    def first_timestamp(self) -> datetime | None:
        return self.entries[0].timestamp if self.entries else None

    @property
    def last_timestamp(self) -> datetime | None:
        return self.entries[-1].timestamp if self.entries else None

    def names(self) -> tuple[str, ...]:
        return tuple(entry.name for entry in self.entries)

    def filter(self, prefix: str) -> "InvestigationTimeline":
        return InvestigationTimeline(
            trace_id=self.trace_id,
            entries=tuple(entry for entry in self.entries if entry.name.startswith(prefix)),
        )


def build_timeline(events: tuple[TraceEvent, ...] | list[TraceEvent]) -> InvestigationTimeline:
    """Convert raw trace events into an ordered investigation timeline."""
    ordered = sorted(events, key=lambda event: event.timestamp)
    if not ordered:
        return InvestigationTimeline(trace_id="", entries=())

    entries: list[TimelineEntry] = []
    for event in ordered:
        duration = None
        if event.name.endswith(".completed") or event.name.endswith(".failed"):
            raw_duration = event.attributes.get("duration_ms")
            if raw_duration is not None:
                try:
                    duration = float(raw_duration)
                except ValueError:
                    duration = None
        entries.append(
            TimelineEntry(
                name=event.name,
                timestamp=event.timestamp,
                duration_ms=duration,
                attributes=dict(event.attributes),
            )
        )
    return InvestigationTimeline(trace_id=ordered[0].trace_id, entries=tuple(entries))


def total_duration(timeline: InvestigationTimeline) -> float:
    """Sum explicit span durations represented in a timeline."""
    return sum(entry.duration_ms or 0.0 for entry in timeline.entries)


def render_timeline(timeline: InvestigationTimeline) -> str:
    """Render a concise text timeline for CLI output and debugging."""
    if not timeline.entries:
        return "No trace events recorded.\n"
    lines = [f"Trace {timeline.trace_id}", ""]
    for entry in timeline.entries:
        suffix = f" ({entry.duration_ms:.2f} ms)" if entry.duration_ms is not None else ""
        lines.append(f"- {entry.timestamp.isoformat()} — {entry.name}{suffix}")
    return "\n".join(lines) + "\n"
