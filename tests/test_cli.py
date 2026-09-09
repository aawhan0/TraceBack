from pathlib import Path

from app.cli import main


def test_cli_scenarios_command(capsys) -> None:
    import sys

    sys.argv = ["traceback", "scenarios"]
    main()
    assert "database-pool-exhaustion" in capsys.readouterr().out


def test_cli_investigate_and_stats_commands(tmp_path: Path, monkeypatch, capsys) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "cli.db"))

    sys.argv = ["traceback", "investigate", "database-pool-exhaustion"]
    main()
    output = capsys.readouterr().out
    assert '"run_id"' in output
    assert '"passed": true' in output

    sys.argv = ["traceback", "stats"]
    main()
    output = capsys.readouterr().out
    assert '"total_runs": 1' in output


def test_cli_benchmark_command_returns_json(tmp_path, capsys, monkeypatch) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "benchmark.db"))
    sys.argv = [
        "traceback",
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


def test_cli_benchmark_report_renders_markdown(tmp_path, capsys, monkeypatch) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "report.db"))
    sys.argv = [
        "traceback",
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
        "traceback",
        "benchmark",
        "--name",
        "history-test",
        "--scenario-id",
        "database-pool-exhaustion",
    ]
    main()
    capsys.readouterr()

    sys.argv = ["traceback", "experiments"]
    main()
    output = capsys.readouterr().out
    assert "history-test" in output


def test_cli_experiment_reports_missing_id(tmp_path, monkeypatch) -> None:
    import sys

    monkeypatch.setenv("TRACEBACK_DATABASE_PATH", str(tmp_path / "missing.db"))
    monkeypatch.setattr(
        sys,
        "argv",
        ["traceback", "experiment", "missing"],
    )
    try:
        main()
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected parser error")
