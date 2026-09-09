from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Protocol

from app.models.domain import Diagnosis, IncidentScenario


@dataclass(frozen=True)
class ProviderRequest:
    """Normalized request sent to an LLM provider."""

    system_prompt: str
    user_prompt: str
    model: str


@dataclass(frozen=True)
class ProviderResponse:
    """Provider output plus transport metadata."""

    text: str
    provider: str
    model: str
    latency_ms: float


class CompletionProvider(Protocol):
    """Minimal provider boundary used by the investigation agent."""

    name: str

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        ...


class ProviderError(RuntimeError):
    """Stable application-level provider failure."""


class ProviderRegistry:
    """Explicit provider registry used by API and agent composition."""

    def __init__(self) -> None:
        self._providers: dict[str, CompletionProvider] = {}

    def register(self, provider: CompletionProvider) -> None:
        if not provider.name.strip():
            raise ValueError("provider name is required")
        if provider.name in self._providers:
            raise ValueError(f"provider already registered: {provider.name}")
        self._providers[provider.name] = provider

    def get(self, name: str) -> CompletionProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise KeyError(f"unknown provider: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._providers))


@dataclass(frozen=True)
class InvestigationContract:
    """Stable contract between orchestration and a diagnosis-producing agent."""

    scenario_id: str
    system_prompt: str
    user_prompt: str

    @classmethod
    def for_scenario(cls, scenario: IncidentScenario) -> InvestigationContract:
        evidence = "\n".join(
            f"- {item.id}: {item.content}" for item in scenario.evidence
        )
        system = (
            "You are an incident investigator. Return only JSON matching the "
            "Diagnosis schema. Ground every claim in supplied evidence."
        )
        user = (
            f"Incident: {scenario.incident.title}\n"
            f"Description: {scenario.incident.description}\n"
            f"Evidence:\n{evidence}"
        )
        return cls(scenario.id, system, user)


def timed_completion(
    provider: CompletionProvider,
    request: ProviderRequest,
) -> ProviderResponse:
    started = monotonic()
    try:
        response = provider.complete(request)
    except Exception as exc:
        raise ProviderError(f"{provider.name} completion failed: {exc}") from exc
    elapsed = (monotonic() - started) * 1000
    if not response.text.strip():
        raise ProviderError(f"{provider.name} returned an empty response")
    return ProviderResponse(
        text=response.text,
        provider=response.provider,
        model=response.model,
        latency_ms=response.latency_ms or elapsed,
    )
