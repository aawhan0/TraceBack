from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class LogContext:
    """Structured fields attached to every application log entry."""

    service: str = "traceback"
    environment: str = "development"

    def with_fields(self, **fields: object) -> dict[str, object]:
        return {
            "service": self.service,
            "environment": self.environment,
            **fields,
        }


class JsonFormatter(logging.Formatter):
    """Compact JSON formatter for production-friendly structured logs."""

    def __init__(self, context: LogContext | None = None) -> None:
        super().__init__()
        self.context = context or LogContext()

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = self.context.with_fields(
            timestamp=datetime.fromtimestamp(record.created).isoformat(),
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
        )
        trace_id = getattr(record, "trace_id", None)
        if trace_id:
            payload["trace_id"] = trace_id
        for key in ("scenario_id", "run_id", "experiment_id"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, sort_keys=True)


def configure_logging(level: int = logging.INFO, context: LogContext | None = None) -> None:
    """Install the application JSON formatter exactly once."""
    root = logging.getLogger()
    root.setLevel(level)
    if not any(isinstance(handler.formatter, JsonFormatter) for handler in root.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter(context))
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class TraceLoggerAdapter(logging.LoggerAdapter[logging.Logger]):
    """Logger adapter that carries a trace ID into structured output."""

    def process(self, msg: object, kwargs: dict[str, object]):
        extra = dict(kwargs.get("extra", {}))
        if self.extra.get("trace_id"):
            extra["trace_id"] = self.extra["trace_id"]
        kwargs["extra"] = extra
        return msg, kwargs


def logger_for_trace(name: str, trace_id: str) -> TraceLoggerAdapter:
    return TraceLoggerAdapter(get_logger(name), {"trace_id": trace_id})
