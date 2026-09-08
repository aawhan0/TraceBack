from pathlib import Path

from app.agent.baseline import BaselineInvestigator
from app.evaluation.evaluator import evaluate_diagnosis
from app.models.domain import InvestigationRun
from app.repository.runs import SQLiteRunStore, utc_now
from app.scenarios.catalog import SCENARIOS
from app.services.investigation import InvestigationService


def test_sqlite_store_round_trips_investigation_run(tmp_path: Path) -> None:
    scenario = SCENARIOS[0]
    diagnosis = BaselineInvestigator(scenario).investigate(scenario.incident)
    evaluation = evaluate_diagnosis(scenario, diagnosis)
    run = InvestigationRun(
        run_id="run-test-001",
        scenario_id=scenario.id,
        mode="baseline",
        provider="baseline",
        diagnosis=diagnosis,
        root_cause_match=evaluation.root_cause_match,
        evidence_recall=evaluation.evidence_recall,
        evidence_precision=evaluation.evidence_precision,
        confidence_valid=evaluation.confidence_valid,
        action_present=evaluation.action_present,
        passed=evaluation.passed,
        duration_ms=12.5,
        created_at=utc_now(),
    )
    store = SQLiteRunStore(str(tmp_path / "runs.db"))
    store.save(run)

    loaded = store.get(run.run_id)
    assert loaded == run
    assert store.list(scenario_id=scenario.id)[0].run_id == run.run_id


def test_store_stats_are_scoped_and_durable(tmp_path: Path) -> None:
    store = SQLiteRunStore(str(tmp_path / "runs.db"))
    first = InvestigationService().investigate(SCENARIOS[0], run_store=store)
    second = InvestigationService().investigate(SCENARIOS[1], run_store=store)

    stats = store.stats(scenario_id=SCENARIOS[0].id)
    assert stats.total_runs == 1
    assert stats.passed_runs == 1
    assert stats.pass_rate == 1.0
    assert stats.average_confidence == first.diagnosis.confidence
    assert stats.average_duration_ms >= 0
    assert store.get(second.run_id) is not None
