from __future__ import annotations

import os
import platform
from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkProvenance:
    """Environment and configuration identity captured with a benchmark."""

    application_version: str
    git_revision: str
    python_version: str
    environment: str
    provider: str
    model: str | None

    @classmethod
    def from_environment(
        cls,
        *,
        provider: str = "baseline",
        model: str | None = None,
        application_version: str = "0.1.0",
    ) -> "BenchmarkProvenance":
        revision = (
            os.getenv("TRACEBACK_GIT_SHA")
            or os.getenv("GITHUB_SHA")
            or "unknown"
        )
        return cls(
            application_version=application_version,
            git_revision=revision,
            python_version=platform.python_version(),
            environment=os.getenv("TRACEBACK_ENVIRONMENT", "development"),
            provider=provider,
            model=model,
        )

    def as_dict(self) -> dict[str, str | None]:
        return {
            "application_version": self.application_version,
            "git_revision": self.git_revision,
            "python_version": self.python_version,
            "environment": self.environment,
            "provider": self.provider,
            "model": self.model,
        }
