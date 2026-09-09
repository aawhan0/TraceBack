import pytest

from app.evaluation.calibration import calibration_report, confidence_standard_error


def test_calibration_report_perfect_confidence_is_well_calibrated() -> None:
    report = calibration_report([(1.0, True), (0.0, False)])
    assert report.observations == 2
    assert report.brier_score == 0.0
    assert report.expected_calibration_error == 0.0
    assert report.maximum_calibration_error == 0.0


def test_calibration_report_exposes_bucket_metrics() -> None:
    report = calibration_report(
        [(0.9, True), (0.8, False), (0.2, False), (0.1, False)],
        bucket_count=5,
    )
    assert len(report.buckets) == 3
    assert report.brier_score > 0
    assert report.expected_calibration_error > 0


@pytest.mark.parametrize("bucket_count", [0, 101])
def test_calibration_report_rejects_invalid_bucket_count(bucket_count: int) -> None:
    with pytest.raises(ValueError, match="bucket_count"):
        calibration_report([(0.5, True)], bucket_count=bucket_count)


def test_calibration_report_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        calibration_report([(1.1, True)])


def test_calibration_report_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="At least one"):
        calibration_report([])


def test_confidence_standard_error() -> None:
    assert confidence_standard_error([0.5]) == 0
    assert confidence_standard_error([0.5, 0.5, 0.5]) == 0
    assert confidence_standard_error([0.0, 1.0]) == pytest.approx(0.5)


def test_confidence_standard_error_validates_input() -> None:
    with pytest.raises(ValueError):
        confidence_standard_error([])
    with pytest.raises(ValueError):
        confidence_standard_error([2.0])
