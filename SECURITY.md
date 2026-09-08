# Security Policy

## Supported Versions

Security fixes are applied to the current development state on the `main` branch. Older commits, forks, and unreleased development versions may not receive security fixes.

## Reporting a Vulnerability

Please do not publicly disclose a suspected security vulnerability in an issue or pull request.

Use GitHub's private vulnerability reporting or security advisory features for this repository when available. If those features are unavailable, contact the maintainer privately through the GitHub profile associated with the repository.

When reporting a vulnerability, include:

- A clear description of the issue.
- The affected component or endpoint.
- Steps to reproduce the issue.
- The potential impact.
- Any suggested mitigation, if known.

Please avoid including real secrets, credentials, personal data, or destructive proof-of-concept payloads.

## Scope

Security reports are especially relevant to:

- MCP tool execution and tool inputs
- incident/evidence ingestion
- LLM provider integrations
- API endpoints
- structured output validation
- local model/runtime interaction
- filesystem or subprocess access
- configuration and secret handling

Traceback is intended as a local-first engineering project. A local deployment should still treat external or untrusted inputs as untrusted.

## LLM and Tool Safety

Traceback may pass incident data to an LLM and may allow an agent to invoke operational tools.

Tool implementations should:

- validate inputs
- constrain available operations
- avoid unnecessary host access
- avoid executing arbitrary user-provided commands
- return structured, attributable evidence
- fail safely when a tool cannot provide trustworthy data

LLM-generated text should not be treated as executable instructions.

## Secrets

Do not commit:

- API keys
- access tokens
- passwords
- private credentials
- production incident data

Use environment variables or local configuration files that are excluded from source control.

Ollama is currently used for local inference, so local development should prefer local models and avoid sending sensitive incident data to external providers unless that provider is explicitly configured and trusted.

## Responsible Disclosure

Security reports are handled privately where possible. Please allow reasonable time for investigation and remediation before public disclosure.
