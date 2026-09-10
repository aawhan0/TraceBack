from pathlib import Path

from app.cli import main


def test_cli_scenarios_command(capsys) -> None:
    import sys

    sys.argv = ["trbk", "scenarios"]
    main()
    assert "database-pool-exhaustion" in capsys.readouterr().out


def test_cli_investigate_and_stats_commands(tmp_path: Path, monkeypatch, capsys) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "cli.db"))

    sys.argv = ["trbk", "investigate", "database-pool-exhaustion"]
    main()
    output = capsys.readouterr().out
    assert '"run_id"' in output
    assert '"passed": true' in output

    sys.argv = ["trbk", "stats"]
    main()
    output = capsys.readouterr().out
    assert '"total_runs": 1' in output


def test_cli_benchmark_command_returns_json(tmp_path, capsys, monkeypatch) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "benchmark.db"))
    sys.argv = [
        "trbk",
        "benchmark",
        "--name",
        "cli-test",
        "--scenario-id",
        "database-pool-exhaustion",
        "--repetitions",
        "2",
    ]
    main()
    output = capsys.readouterr().out
    assert '"experiment_id"' in output
    assert '"regression_passed": true' in output
    assert '"pass_rate": 1.0' in output
    assert '"root_cause_accuracy": 1.0' in output
    assert '"average_evidence_recall": 1.0' in output
    assert '"average_evidence_precision": 1.0' in output


def test_cli_benchmark_report_renders_markdown(tmp_path, capsys, monkeypatch) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "report.db"))
    sys.argv = [
        "trbk",
        "benchmark",
        "--name",
        "report-test",
        "--scenario-id",
        "database-pool-exhaustion",
        "--report",
    ]
    main()
    output = capsys.readouterr().out
    assert "# Experiment: report-test" in output
    assert "**Status:** PASS" in output


def test_cli_experiments_lists_history(tmp_path, capsys, monkeypatch) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "history.db"))
    sys.argv = [
        "trbk",
        "benchmark",
        "--name",
        "history-test",
        "--scenario-id",
        "database-pool-exhaustion",
    ]
    main()
    capsys.readouterr()

    sys.argv = ["trbk", "experiments"]
    main()
    output = capsys.readouterr().out
    assert "history-test" in output


def test_cli_experiment_reports_missing_id(tmp_path, monkeypatch) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "missing.db"))
    monkeypatch.setattr(
        sys,
        "argv",
        ["trbk", "experiment", "missing"],
    )
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected parser error")


def test_compare_command_outputs_structured_delta(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "cli-compare.db"))
    from app.cli import main
    import sys

    # Seed two compatible experiments through the CLI benchmark path.
    for name in ("cli-base", "cli-candidate"):
        monkeypatch.setattr(sys, "argv", ["trbk", "benchmark", "--name", name])
        main()

    # Read the persisted IDs from the store so the command mirrors real usage.
    from app.services.benchmark import BenchmarkService
    records = BenchmarkService().list()
    ids = {record.name: record.experiment_id for record in records}

    monkeypatch.setattr(
        sys,
        "argv",
        ["trbk", "compare", ids["cli-base"], ids["cli-candidate"]],
    )
    main()
    output = capsys.readouterr().out
    assert '"verdict": "unchanged"' in output
    assert '"pass_rate"' in output
    assert '"root_cause_accuracy"' in output
