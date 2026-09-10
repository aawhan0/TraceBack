# MCP Evidence Sources

TraceBack can extend its evidence layer with operator-configured remote MCP servers while keeping the investigation agent's tool surface constrained.

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

Each configured source requires:

- a stable lowercase source `id`
- an `http` or `https` MCP endpoint
- a remote tool that follows TraceBack's structured evidence contract

The integration is explicitly operator-configured. The model cannot invent a source or choose an arbitrary remote tool.

## Evidence contract

The configured remote tool is called with a narrow operation contract:

- `scenario_id`
- `operation`: `list`, `get`, or `search`
- `evidence_id`
- `query`

Responses contain structured evidence objects with:

- `id`
- `source`
- `kind`
- `content`

TraceBack preserves external attribution by attaching the configured source identity to downstream evidence.

## MCP tools

The MCP server exposes:

| Tool | Purpose |
| --- | --- |
| `get_incident_evidence` | Retrieve evidence from built-in and persisted scenarios |
| `list_evidence_sources` | Inspect configured remote source metadata |
| `get_custom_evidence` | Read evidence from one configured remote source |

The boundary is intentionally narrow: TraceBack does not forward arbitrary model-supplied tool names or arbitrary arguments.

## Security boundary

Remote source configuration is controlled by the operator. The application validates source IDs and URLs, requires HTTP(S), rejects duplicate IDs, and caps the registry at 20 sources.

TraceBack does not execute remote commands, read arbitrary local files through this integration, or expose authentication secrets in source configuration. Endpoint reachability and trust remain deployment responsibilities.

Authentication, OAuth, write-capable tools, and broader remote-tool orchestration are intentionally outside this feature's scope.

## Local testing

The built-in MCP server can be launched with:

```powershell
python -m app.mcp.server
```

For Inspector-based development:

```powershell
mcp dev app/mcp/server.py
```

See the main [README](../README.md) for the overall architecture and local setup.
