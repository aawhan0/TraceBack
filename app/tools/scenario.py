from app.agent.contracts import ToolRequest, ToolResponse
from app.models.domain import IncidentScenario


class ScenarioEvidenceTool:
    """Expose scenario evidence through a constrained tool boundary.

    ``list`` returns metadata only (id/source/kind). Callers must ``get`` or
    ``search`` to read full evidence content.
    """

    name = "scenario_evidence"
    _allowed_operations = frozenset({"list", "get", "search"})

    def __init__(self, scenario: IncidentScenario) -> None:
        self._evidence = {item.id: item for item in scenario.evidence}

    def execute(self, request: ToolRequest) -> ToolResponse:
        if request.name != self.name:
            raise ValueError(f"Unsupported tool request: {request.name}")

        operation = request.arguments.get("operation", "list")
        if operation not in self._allowed_operations:
            raise ValueError(f"Unsupported evidence operation: {operation}")

        if operation == "list":
            # Metadata only: callers must get/search to read full content.
            evidence = tuple(
                item.model_copy(update={"content": ""}) for item in self._evidence.values()
            )
        elif operation == "get":
            evidence_id = request.arguments.get("evidence_id", "")
            item = self._evidence.get(evidence_id)
            evidence = (item,) if item is not None else ()
        else:
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

        return ToolResponse(tool_name=self.name, evidence=evidence)
