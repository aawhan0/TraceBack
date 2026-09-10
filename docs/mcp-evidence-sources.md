# MCP Evidence Sources

Traceback can aggregate evidence from operator-configured remote MCP servers without giving the investigation agent arbitrary tool access.

## Configuration

Set `TRACEBACK_MCP_EVIDENCE_SOURCES` to a JSON list:

```json
[
  {
    "id": "payments",
    "url": "https://example.internal/mcp",
    "tool": "get_incident_evidence"
  }
]
```

Each source must have:

- a stable lowercase `id`
- an `http` or `https` MCP endpoint
- a tool that implements the Traceback evidence contract

The configured tool is called with only these arguments:

- `scenario_id`
- `operation`: `list`, `get`, or `search`
- `evidence_id`
- `query`

The remote tool must return a structured list of evidence objects containing `id`, `source`, `kind`, and `content`. Traceback adds `external_source` so the origin remains attributable in downstream results.

## MCP tools

The server exposes three tools:

- `get_incident_evidence` — built-in and persisted scenario evidence
- `list_evidence_sources` — configured remote source metadata
- `get_custom_evidence` — read-only retrieval from one configured remote source

This keeps the MCP boundary explicit: Traceback never forwards arbitrary tool names or arbitrary arguments supplied by the model.

## Security boundary

Remote source configuration is operator-controlled. URLs are restricted to HTTP(S), source IDs are unique, and the registry is capped at 20 sources.

Traceback does not execute remote commands, read arbitrary local files, or expose authentication secrets through the source configuration. Network reachability and trust of configured endpoints remain deployment responsibilities.

The feature is intentionally narrow. Authentication, OAuth, and write-capable remote tools should be added as separate capabilities with their own validation and tests.
