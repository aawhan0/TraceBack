from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.config import Settings
from app.repository.runs import SQLiteRunStore
from app.scenarios.catalog import all_scenarios

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class KnowledgeEntry(BaseModel):
    scenario_id: str
    title: str
    description: str
    root_cause: str
    evidence_count: int = Field(ge=0)
    required_evidence_ids: list[str]
    latest_run_id: str | None = None
    latest_run_passed: bool | None = None
    latest_run_confidence: float | None = Field(default=None, ge=0, le=1)
    latest_run_at: str | None = None
    matched_terms: list[str] = Field(default_factory=list)


def _score(scenario, query: str) -> tuple[int, list[str]]:
    if not query.strip():
        return 0, []
    haystack = " ".join(
        [
            scenario.id,
            scenario.incident.title,
            scenario.incident.description,
            scenario.expected_root_cause,
            *scenario.root_cause_keywords,
            *(item.source for item in scenario.evidence),
            *(item.kind for item in scenario.evidence),
            *(item.content for item in scenario.evidence),
        ]
    ).casefold()
    terms = [term for term in query.casefold().split() if term]
    matched = list(dict.fromkeys(term for term in terms if term in haystack))
    return len(matched), matched


@router.get("", response_model=list[KnowledgeEntry])
def search_knowledge(
    q: str = Query(default="", max_length=200),
    limit: int = Query(default=20, ge=1, le=50),
) -> list[KnowledgeEntry]:
    scenarios = all_scenarios()
    store = SQLiteRunStore(Settings.from_environment().database_path)
    ranked: list[tuple[int, object, list[str]]] = []
    for scenario in scenarios:
        score, matched = _score(scenario, q)
        if q.strip() and score == 0:
            continue
        ranked.append((score, scenario, matched))

    ranked.sort(key=lambda item: (-item[0], item[1].incident.title.casefold()))
    entries: list[KnowledgeEntry] = []
    for _, scenario, matched in ranked[:limit]:
        latest = next(iter(store.list(scenario_id=scenario.id, limit=1)), None)
        entries.append(
            KnowledgeEntry(
                scenario_id=scenario.id,
                title=scenario.incident.title,
                description=scenario.incident.description,
                root_cause=scenario.expected_root_cause,
                evidence_count=len(scenario.evidence),
                required_evidence_ids=scenario.required_evidence_ids,
                latest_run_id=latest.run_id if latest else None,
                latest_run_passed=latest.passed if latest else None,
                latest_run_confidence=latest.confidence if latest else None,
                latest_run_at=latest.created_at.isoformat() if latest else None,
                matched_terms=matched,
            )
        )
    return entries
