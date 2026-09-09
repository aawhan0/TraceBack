from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Cursor:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("cursor cannot be empty")


@dataclass(frozen=True)
class Page[T]:
    items: tuple[T, ...]
    next_cursor: Cursor | None
    limit: int

    def as_dict(self, serializer) -> dict[str, Any]:
        return {
            "items": [serializer(item) for item in self.items],
            "next_cursor": self.next_cursor.value if self.next_cursor else None,
            "limit": self.limit,
        }


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
