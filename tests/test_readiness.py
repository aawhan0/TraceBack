from app.services.health import ReadinessChecker


def test_readiness_reports_healthy_dependencies() -> None:
    report = ReadinessChecker({"database": lambda: "ok"}).check()
    assert report.ready is True
    assert report.dependencies[0].healthy is True


def test_readiness_reports_dependency_failure() -> None:
    def fail() -> str:
        raise RuntimeError("database unavailable")

    report = ReadinessChecker({"database": fail}).check()
    assert report.ready is False
    assert report.dependencies[0].detail == "database unavailable"
