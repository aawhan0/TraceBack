import pytest
from pydantic import ValidationError

from app.api.pagination import PaginationParams


def test_pagination_defaults_are_bounded() -> None:
    params = PaginationParams()
    assert params.limit == 50
    assert params.offset == 0


def test_pagination_accepts_valid_values() -> None:
    params = PaginationParams(limit=200, offset=10)
    assert params.limit == 200
    assert params.offset == 10


@pytest.mark.parametrize("value", [0, -1, 201])
def test_pagination_rejects_invalid_limit(value: int) -> None:
    with pytest.raises(ValidationError):
        PaginationParams(limit=value)


def test_pagination_rejects_negative_offset() -> None:
    with pytest.raises(ValidationError):
        PaginationParams(offset=-1)
