from mcp.server import MCPServer

from app.mcp.sources import fetch_source_evidence, load_sources
from app.scenarios.catalog import get_scenario

mcp = MCPServer(
    "Traceback Evidence",
    instructions="Expose version-controlled and operator-configured incident evidence to investigation agents.",
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


@mcp.tool()
async def get_custom_evidence(
    source_id: str,
    scenario_id: str,
    operation: str = "list",
    evidence_id: str = "",
    query: str = "",
) -> list[dict[str, object]]:
    """Retrieve evidence from an operator-configured remote MCP source."""
    if operation not in {"list", "get", "search"}:
        raise ValueError("Unsupported evidence operation")

    source = next((item for item in load_sources() if item.id == source_id), None)
    if source is None:
        raise ValueError(f"Unknown MCP evidence source: {source_id}")

    return await fetch_source_evidence(
        source,
        scenario_id=scenario_id,
        operation=operation,
        evidence_id=evidence_id,
        query=query,
    )


@mcp.tool()
def list_evidence_sources() -> list[dict[str, str]]:
    """List the operator-configured remote MCP evidence sources."""
    return [{"id": source.id, "url": source.url, "tool": source.tool} for source in load_sources()]


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
