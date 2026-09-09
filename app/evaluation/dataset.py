from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable

from app.models.domain import IncidentScenario


@dataclass(frozen=True)
class DatasetCase:
    """A versioned reference to an incident scenario."""

    scenario_id: str
    tags: tuple[str, ...] = ()
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ValueError("scenario_id is required")
        if self.weight <= 0:
            raise ValueError("case weight must be positive")
        normalized = tuple(sorted({tag.strip().casefold() for tag in self.tags if tag.strip()}))
        object.__setattr__(self, "tags", normalized)


@dataclass(frozen=True)
class DatasetManifest:
    """Immutable benchmark dataset manifest."""

    name: str
    version: str
    cases: tuple[DatasetCase, ...]
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("dataset name is required")
        if not self.version.strip():
            raise ValueError("dataset version is required")
        if not self.cases:
            raise ValueError("dataset must contain at least one case")
        ids = [case.scenario_id for case in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("dataset cannot contain duplicate scenario IDs")

    @property
    def case_count(self) -> int:
        return len(self.cases)

    @property
    def fingerprint(self) -> str:
        payload = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "cases": [
                {
                    "scenario_id": case.scenario_id,
                    "tags": case.tags,
                    "weight": case.weight,
                }
                for case in self.cases
            ],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return sha256(encoded).hexdigest()

    def select(
        self,
        *,
        scenario_ids: Iterable[str] | None = None,
        tags: Iterable[str] | None = None,
    ) -> "DatasetManifest":
        ids = {value for value in scenario_ids or ()}
        wanted_tags = {value.strip().casefold() for value in tags or () if value.strip()}
        selected = tuple(
            case
            for case in self.cases
            if (not ids or case.scenario_id in ids)
            and (not wanted_tags or wanted_tags.issubset(set(case.tags)))
        )
        if not selected:
            raise ValueError("dataset selection produced no cases")
        return DatasetManifest(
            name=self.name,
            version=self.version,
            cases=selected,
            description=self.description,
        )

    def scenarios(self, catalog: dict[str, IncidentScenario]) -> tuple[IncidentScenario, ...]:
        missing = [case.scenario_id for case in self.cases if case.scenario_id not in catalog]
        if missing:
            raise KeyError(f"Unknown dataset scenarios: {', '.join(missing)}")
        return tuple(catalog[case.scenario_id] for case in self.cases)


def build_manifest(
    name: str,
    version: str,
    scenarios: Iterable[IncidentScenario],
    *,
    tags: dict[str, Iterable[str]] | None = None,
    description: str = "",
) -> DatasetManifest:
    tag_map = tags or {}
    cases = tuple(
        DatasetCase(scenario.id, tuple(tag_map.get(scenario.id, ())))
        for scenario in scenarios
    )
    return DatasetManifest(name=name, version=version, cases=cases, description=description)


def manifest_to_json(manifest: DatasetManifest) -> str:
    return json.dumps(
        {
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "fingerprint": manifest.fingerprint,
            "cases": [
                {
                    "scenario_id": case.scenario_id,
                    "tags": list(case.tags),
                    "weight": case.weight,
                }
                for case in manifest.cases
            ],
        },
        indent=2,
        sort_keys=True,
    )
