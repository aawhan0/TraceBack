import pytest

from app.tools.registry import ToolRegistry


class DummyTool:
    name = "dummy"

    def execute(self, request):
        return request


def test_registry_registers_and_resolves_tools() -> None:
    registry = ToolRegistry([DummyTool()])
    assert registry.names() == ("dummy",)
    assert registry.get("dummy").name == "dummy"


def test_registry_rejects_duplicates_and_unknown_tools() -> None:
    registry = ToolRegistry([DummyTool()])
    with pytest.raises(ValueError, match="already registered"):
        registry.register(DummyTool())
    with pytest.raises(KeyError, match="Unknown investigation tool"):
        registry.get("missing")
