import json
from datetime import datetime, timezone
from typing import Any


def json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "__dict__"):
        return value.__dict__
    raise TypeError(f"cannot serialize {type(value).__name__}")


def dumps(payload: Any) -> str:
    return json.dumps(
        payload,
        default=json_default,
        sort_keys=True,
        separators=(",", ":"),
    )
