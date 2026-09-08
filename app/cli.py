import argparse
import json

from app.config import Settings
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

    runs = subparsers.add_parser("runs", help="List persisted investigation runs.")
    runs.add_argument("--scenario-id")
    runs.add_argument("--limit", type=int, default=20)

    show = subparsers.add_parser("show", help="Show one persisted investigation run.")
    show.add_argument("run_id")

    args = parser.parse_args()
    settings = Settings.from_environment()
    store = SQLiteRunStore(settings.database_path)

    if args.command == "scenarios":
        _json([{"id": item.id, "title": item.incident.title} for item in SCENARIOS])
        return

    if args.command == "runs":
        _json([item.model_dump(mode="json") for item in store.list(args.scenario_id, args.limit)])
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
