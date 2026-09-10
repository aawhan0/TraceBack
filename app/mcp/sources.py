from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlparse

from mcp import Client
from pydantic import BaseModel, Field


class EvidenceSource(BaseModel):
    """Operator-configured remote MCP server exposing the Traceback evidence contract."""

    id: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    url: str = Field(min_length=1, max_length=500)
    tool: str = Field(default="get_incident_evidence", min_length=1, max_length=100)

    def validate_url(self) -> None:
        parsed = urlparse(self.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Unsupported MCP source URL: {self.url}")


def load_sources(raw: str | None = None) -> list[EvidenceSource]:
    """Load bounded remote MCP evidence sources from operator configuration."""
    value = os.getenv("TRACEBACK_MCP_EVIDENCE_SOURCES", "") if raw is None else raw
    if not value.strip():
        return []

    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError("TRACEBACK_MCP_EVIDENCE_SOURCES must be valid JSON") from exc

    if not isinstance(payload, list) or len(payload) > 20:
        raise ValueError("TRACEBACK_MCP_EVIDENCE_SOURCES must be a JSON list of at most 20 sources")

    sources = [EvidenceSource.model_validate(item) for item in payload]
    ids = [source.id for source in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("MCP evidence source IDs must be unique")
    for source in sources:
        source.validate_url()
    return sources


async def fetch_source_evidence(
    source: EvidenceSource,
    *,
    scenario_id: str,
    operation: str,
    evidence_id: str = "",
    query: str = "",
) -> list[dict[str, Any]]:
    """Call a configured MCP source using Traceback's read-only evidence contract."""
    arguments = {
        "scenario_id": scenario_id,
        "operation": operation,
        "evidence_id": evidence_id,
        "query": query,
    }
    async with Client(source.url) as client:
        result = await client.session.call_tool(source.tool, arguments=arguments)

    if result.is_error:
        raise ValueError(f"MCP evidence source '{source.id}' returned an error")
    structured = result.structured_content or {}
    evidence = structured.get("result")
    if not isinstance(evidence, list):
        raise ValueError(f"MCP evidence source '{source.id}' returned an invalid evidence payload")

    normalized: list[dict[str, Any]] = []
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError(f"MCP evidence source '{source.id}' returned a non-object evidence item")
        required = {"id", "source", "kind", "content"}
        if not required.issubset(item):
            raise ValueError(f"MCP evidence source '{source.id}' returned incomplete evidence")
        normalized.append({**item, "external_source": source.id})
    return normalized
