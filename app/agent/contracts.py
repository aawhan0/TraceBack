from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from app.models.domain import Evidence, Incident


@dataclass(frozen=True)
class ToolRequest:
    name: str
    arguments: Mapping[str, str]


@dataclass(frozen=True)
class ToolResponse:
    tool_name: str
    evidence: tuple[Evidence, ...]
    message: str = ""


class InvestigationTool(Protocol):
    name: str

    def execute(self, request: ToolRequest) -> ToolResponse:
        """Execute a constrained investigation operation."""


class Investigator(Protocol):
    def investigate(self, incident: Incident) -> object:
        """Investigate an incident and return a structured diagnosis."""
