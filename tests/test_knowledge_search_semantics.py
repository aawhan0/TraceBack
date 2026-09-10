from app.api.knowledge import _score
from app.scenarios.catalog import all_scenarios


def test_knowledge_score_requires_every_query_term() -> None:
    redis = next(item for item in all_scenarios() if item.id == "redis-connectivity-failure")

    score, matched = _score(redis, "unknown failure pattern")

    assert score == 0
    assert matched == []


def test_knowledge_score_preserves_multi_term_match() -> None:
    database = next(item for item in all_scenarios() if item.id == "database-pool-exhaustion")

    score, matched = _score(database, "connection pool")

    assert score == 2
    assert matched == ["connection", "pool"]
