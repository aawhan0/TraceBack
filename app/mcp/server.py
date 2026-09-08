from mcp.server import MCPServer

from app.scenarios.catalog import get_scenario

mcp = MCPServer(
    "Traceback Evidence",
    instructions="Expose version-controlled incident evidence to investigation agents.",
)


@mcp.tool()
def get_incident_evidence(
    scenario_id: str,
    operation: str = "list",
    evidence_id: str = "",
    query: str = "",
) -> list[dict[str, object]]:
    """Retrieve attributable evidence for a Traceback incident scenario."""
    scenario = get_scenario(scenario_id)
    if operation not in {"list", "get", "search"}:
        raise ValueError("Unsupported evidence operation")

    if operation == "list":
        evidence = scenario.evidence
    elif operation == "get":
        evidence = [item for item in scenario.evidence if item.id == evidence_id]
    else:
        normalized = query.strip().casefold()
        evidence = [
            item
            for item in scenario.evidence
            if normalized
            and (
                normalized in item.content.casefold()
                or normalized in item.source.casefold()
                or normalized in item.kind.casefold()
            )
        ]

    return [
        {
            "id": item.id,
            "source": item.source,
            "kind": item.kind,
            "content": item.content,
            "timestamp": item.timestamp.isoformat() if item.timestamp else None,
        }
        for item in evidence
    ]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
