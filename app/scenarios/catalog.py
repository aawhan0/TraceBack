from app.models.domain import Evidence
from app.models.domain import Incident
from app.models.domain import IncidentScenario


DATABASE_POOL_EXHAUSTION = IncidentScenario(
    id="database-pool-exhaustion",
    incident=Incident(
        id="inc-001",
        title="API latency spike and 500 errors",
        description="Checkout requests are timing out while database-backed API calls return 500s.",
        status="investigating",
    ),
    evidence=[
        Evidence(
            id="ev-db-001",
            source="api",
            kind="logs",
            content="checkout-api: timeout acquiring database connection from pool",
        ),
        Evidence(
            id="ev-db-002",
            source="database",
            kind="metrics",
            content="database active connections at configured pool maximum",
        ),
        Evidence(
            id="ev-db-003",
            source="api",
            kind="logs",
            content="checkout-api: requests waiting for database connections",
        ),
    ],
    expected_root_cause="Database connection pool exhaustion",
    root_cause_keywords=["database", "connection pool", "exhaustion"],
    required_evidence_ids=["ev-db-001", "ev-db-002"],
)


REDIS_CONNECTIVITY_FAILURE = IncidentScenario(
    id="redis-connectivity-failure",
    incident=Incident(
        id="inc-002",
        title="Session lookups failing",
        description="Requests intermittently fail when the API attempts to access Redis.",
        status="investigating",
    ),
    evidence=[
        Evidence(
            id="ev-redis-001",
            source="api",
            kind="logs",
            content="session-service: Redis connection refused",
        ),
        Evidence(
            id="ev-redis-002",
            source="redis",
            kind="metrics",
            content="Redis connection failures increased sharply after network change",
        ),
        Evidence(
            id="ev-redis-003",
            source="network",
            kind="events",
            content="network policy changed for the application namespace",
        ),
    ],
    expected_root_cause="Redis connectivity failure caused by network policy",
    root_cause_keywords=["redis", "connectivity", "network policy"],
    required_evidence_ids=["ev-redis-001", "ev-redis-003"],
)


RUNAWAY_WORKER_CPU = IncidentScenario(
    id="runaway-worker-cpu",
    incident=Incident(
        id="inc-003",
        title="Worker fleet CPU saturation",
        description="Background workers are consuming sustained CPU and processing jobs slowly.",
        status="investigating",
    ),
    evidence=[
        Evidence(
            id="ev-cpu-001",
            source="worker",
            kind="metrics",
            content="worker CPU remains above 95% across the fleet",
        ),
        Evidence(
            id="ev-cpu-002",
            source="worker",
            kind="logs",
            content="worker: repeated retry loop processing the same failed job",
        ),
        Evidence(
            id="ev-cpu-003",
            source="queue",
            kind="metrics",
            content="queue depth grows while worker throughput declines",
        ),
    ],
    expected_root_cause="Runaway worker retry loop",
    root_cause_keywords=["worker", "retry loop"],
    required_evidence_ids=["ev-cpu-001", "ev-cpu-002"],
)


SCENARIOS = (
    DATABASE_POOL_EXHAUSTION,
    REDIS_CONNECTIVITY_FAILURE,
    RUNAWAY_WORKER_CPU,
)


def get_scenario(scenario_id: str) -> IncidentScenario:
    for scenario in SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    raise KeyError(f"Unknown scenario: {scenario_id}")
