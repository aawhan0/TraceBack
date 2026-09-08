import json

from app.agent.contracts import LLMProvider


class MockLLMProvider:
    """Deterministic provider for tests and offline development."""

    name = "mock"

    def __init__(self, response: dict[str, object]) -> None:
        self._response = response

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        return json.dumps(self._response)
