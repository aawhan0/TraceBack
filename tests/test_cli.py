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
