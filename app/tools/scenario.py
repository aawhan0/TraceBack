from app.agent.contracts import ToolRequest, ToolResponse
from app.models.domain import Evidence, IncidentScenario


class ScenarioEvidenceTool:
    """Expose scenario evidence through a small, MCP-friendly tool boundary."""

    name = "scenario_evidence"

    def __init__(self, scenario: IncidentScenario) -> None:
        self._scenario = scenario
        self._evidence = {item.id: item for item in scenario.evidence}

    def execute(self, request: ToolRequest) -> ToolResponse:
        if request.name != self.name:
            raise ValueError(f"Unsupported tool request: {request.name}")

        operation = request.arguments.get("operation", "list")
        if operation == "list":
            evidence = tuple(self._evidence.values())
        elif operation == "get":
            evidence_id = request.arguments.get("evidence_id", "")
            item = self._evidence.get(evidence_id)
            evidence = (item,) if item is not None else ()
        elif operation == "search":
            query = request.arguments.get("query", "").strip().casefold()
            evidence = tuple(
                item
                for item in self._evidence.values()
                if query
                and (
                    query in item.content.casefold()
                    or query in item.source.casefold()
                    or query in item.kind.casefold()
                )
            )
        else:
            raise ValueError(f"Unsupported evidence operation: {operation}")

        return ToolResponse(tool_name=self.name, evidence=evidence)
