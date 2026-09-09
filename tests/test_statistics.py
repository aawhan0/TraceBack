import pytest

from app.evaluation.statistics import (
    pass_rate_interval,
    percentile,
    proportion_interval,
    summarize,
)


def test_summarize_basic_distribution() -> None:
    result = summarize([1, 2, 3, 4, 5])
    assert result.count == 5
    assert result.minimum == 1
    assert result.maximum == 5
    assert result.mean == 3
    assert result.median == 3
    assert result.p95 == 4.8


def test_summarize_accepts_generators() -> None:
    result = summarize(value for value in range(10))
    assert result.count == 10
    assert result.mean == pytest.approx(4.5)


def test_summarize_rejects_empty_values() -> None:
    with pytest.raises(ValueError, match="At least one"):
        summarize([])


@pytest.mark.parametrize("quantile, expected", [(0, 1), (0.5, 3), (1, 5)])
def test_percentile_boundaries(quantile: float, expected: float) -> None:
    assert percentile([1, 2, 3, 4, 5], quantile) == expected


def test_percentile_interpolates() -> None:
    assert percentile([0, 10], 0.25) == 2.5


def test_percentile_rejects_invalid_quantile() -> None:
    with pytest.raises(ValueError, match="quantile"):
        percentile([1, 2], 1.1)


def test_proportion_interval_bounds_are_valid() -> None:
    interval = proportion_interval(8, 10)
    assert interval.proportion == 0.8
    assert 0 <= interval.lower <= interval.proportion
    assert interval.proportion <= interval.upper <= 1


def test_perfect_proportion_has_upper_bound_one() -> None:
    interval = pass_rate_interval(10, 10)
    assert interval.proportion == 1.0
    assert interval.upper == 1.0


@pytest.mark.parametrize(
    "successes, observations",
    [(-1, 10), (11, 10), (1, 0)],
)
def test_proportion_interval_rejects_invalid_counts(successes: int, observations: int) -> None:
    with pytest.raises(ValueError):
        proportion_interval(successes, observations)


def test_proportion_interval_rejects_non_positive_z() -> None:
    with pytest.raises(ValueError, match="z"):
        proportion_interval(1, 2, z=0)
