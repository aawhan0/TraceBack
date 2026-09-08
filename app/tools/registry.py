from app.agent.contracts import InvestigationTool


class ToolRegistry:
    """Explicit registry for the tools an investigator is allowed to call."""

    def __init__(self, tools: list[InvestigationTool] | None = None) -> None:
        self._tools: dict[str, InvestigationTool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: InvestigationTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> InvestigationTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown investigation tool: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._tools)
