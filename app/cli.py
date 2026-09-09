import argparse
import json

from app.config import Settings
from app.evaluation.dataset import build_manifest
from app.evaluation.markdown import render_experiment_markdown
from app.evaluation.regression import RegressionPolicy
from app.services.benchmark import BenchmarkRequest, BenchmarkService
from app.providers.ollama import OllamaProvider
from app.repository.runs import SQLiteRunStore
from app.scenarios.catalog import SCENARIOS, get_scenario
from app.services.investigation import InvestigationService


def _json(data: object) -> None:
    print(json.dumps(data, indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="traceback",
        description="Investigate production-like incidents and inspect evaluation runs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("scenarios", help="List available incident scenarios.")

    investigate = subparsers.add_parser("investigate", help="Run an investigation.")
    investigate.add_argument("scenario_id")
    investigate.add_argument("--mode", choices=("baseline", "llm"), default="baseline")
    investigate.add_argument("--model")

    benchmark = subparsers.add_parser("benchmark", help="Run a repeatable experiment across scenarios.")
    benchmark.add_argument("--scenario-id", action="append", dest="scenario_ids")
    benchmark.add_argument("--repetitions", type=int, default=1)
    benchmark.add_argument("--name", default="cli-benchmark")
    benchmark.add_argument("--min-pass-rate", type=float, default=1.0)
    benchmark.add_argument("--report", action="store_true", help="Render a Markdown benchmark report.")

    experiments = subparsers.add_parser("experiments", help="List persisted benchmark experiments.")
    experiments.add_argument("--limit", type=int, default=20)
    experiment = subparsers.add_parser("experiment", help="Show one persisted benchmark experiment.")
    experiment.add_argument("experiment_id")

    runs = subparsers.add_parser("runs", help="List persisted investigation runs.")
    runs.add_argument("--scenario-id")
    runs.add_argument("--limit", type=int, default=20)

    stats = subparsers.add_parser("stats", help="Show aggregate persisted run statistics.")
    stats.add_argument("--scenario-id")

    show = subparsers.add_parser("show", help="Show one persisted investigation run.")
    show.add_argument("run_id")

    args = parser.parse_args()
    settings = Settings.from_environment()
    store = SQLiteRunStore(settings.database_path)

    if args.command == "scenarios":
        _json([{"id": item.id, "title": item.incident.title} for item in SCENARIOS])
        return

    if args.command == "benchmark":
        catalog = {scenario.id: scenario for scenario in SCENARIOS}
        scenario_ids = tuple(args.scenario_ids or catalog)
        try:
            selected = [catalog[scenario_id] for scenario_id in scenario_ids]
            dataset = build_manifest(args.name, "cli", selected)
            result = BenchmarkService().run(
                BenchmarkRequest(
                    args.name,
                    dataset,
                    args.repetitions,
                    RegressionPolicy(minimum_pass_rate=args.min_pass_rate),
                ),
                catalog,
            )
        except (KeyError, ValueError, RuntimeError) as exc:
            parser.error(str(exc))
        if args.report:
            print(render_experiment_markdown(result.result, result.regression))
        else:
            _json({
                "experiment_id": result.experiment_id,
                **result.result.__dict__,
                "regression_passed": result.regression.passed,
                "regression_failures": [failure.__dict__ for failure in result.regression.failures],
                "dataset_fingerprint": result.dataset_fingerprint,
            })
        return

    if args.command == "experiments":
        try:
            records = BenchmarkService().list(args.limit)
        except ValueError as exc:
            parser.error(str(exc))
        _json([
            {
                "experiment_id": record.experiment_id,
                "name": record.name,
                "dataset": f"{record.dataset_name}@{record.dataset_version}",
                "pass_rate": record.result.pass_rate,
                "regression_passed": record.regression.passed if record.regression else None,
                "created_at": record.created_at,
            }
            for record in records
        ])
        return

    if args.command == "experiment":
        record = BenchmarkService().get(args.experiment_id)
        if record is None:
            parser.error(f"Experiment not found: {args.experiment_id}")
        _json({
            "experiment_id": record.experiment_id,
            "name": record.name,
            "dataset_name": record.dataset_name,
            "dataset_version": record.dataset_version,
            "dataset_fingerprint": record.dataset_fingerprint,
            "result": record.result.__dict__,
            "regression": (
                {
                    "passed": record.regression.passed,
                    "failures": [failure.__dict__ for failure in record.regression.failures],
                }
                if record.regression
                else None
            ),
            "created_at": record.created_at,
        })
        return

    if args.command == "runs":
        _json([item.model_dump(mode="json") for item in store.list(args.scenario_id, args.limit)])
        return

    if args.command == "stats":
        _json(store.stats(scenario_id=args.scenario_id).model_dump(mode="json"))
        return

    if args.command == "show":
        run = store.get(args.run_id)
        if run is None:
            parser.error(f"Investigation run not found: {args.run_id}")
        _json(run.model_dump(mode="json"))
        return

    try:
        scenario = get_scenario(args.scenario_id)
    except KeyError as exc:
        parser.error(str(exc))

    provider = None
    if args.mode == "llm":
        provider = OllamaProvider(
            model=args.model or settings.model,
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_timeout,
        )

    try:
        result = InvestigationService().investigate(
            scenario,
            provider=provider,
            run_store=store,
        )
    except (RuntimeError, ValueError) as exc:
        parser.error(str(exc))

    _json(
        {
            "run_id": result.run_id,
            "scenario_id": result.scenario_id,
            "mode": args.mode,
            "provider": getattr(provider, "name", "baseline"),
            "diagnosis": result.diagnosis.model_dump(mode="json"),
            "evaluation": {
                "root_cause_match": result.evaluation.root_cause_match,
                "evidence_recall": result.evaluation.evidence_recall,
                "evidence_precision": result.evaluation.evidence_precision,
                "confidence_valid": result.evaluation.confidence_valid,
                "action_present": result.evaluation.action_present,
                "passed": result.evaluation.passed,
            },
            "duration_ms": result.duration_ms,
            "created_at": result.created_at,
        }
    )


if __name__ == "__main__":
    main()
