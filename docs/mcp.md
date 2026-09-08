# MCP Evidence Server

Traceback now includes a real MCP server built with the official Python SDK.

## Tool

The server exposes one constrained tool:

get_incident_evidence

Arguments:

- scenario_id
- operation: list, get, or search
- evidence_id for get
- query for search

The tool returns structured, attributable evidence with stable IDs.

## Local development

The server defaults to stdio:

python -m app.mcp.server

For MCP Inspector development, install the development extra and run:

mcp dev app/mcp/server.py

The official SDK also supports Streamable HTTP when a networked MCP endpoint is needed.

## Security boundary

The current tool can only read version-controlled scenario evidence. It does not execute shell commands, read arbitrary files, or accept executable instructions.

That narrow boundary is intentional. Future operational tools should be added one at a time with explicit input validation and tests.

## Why MCP is separate from FastAPI

FastAPI is the application's service API.

MCP is the model-facing tool protocol.

Keeping those interfaces separate lets an MCP-capable host discover and call investigation tools without coupling the agent to the application's REST endpoints.
