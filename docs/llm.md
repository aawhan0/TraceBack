# LLM Investigation

Traceback now has a real provider boundary for model-backed investigation.

## Flow

1. Select an incident scenario.
2. Build a constrained investigation prompt.
3. Retrieve attributable evidence through the investigation tool boundary.
4. Give the model the incident and evidence.
5. Parse the response into the Diagnosis Pydantic model.
6. Reject malformed or cross-incident output.
7. Run the same deterministic evaluator used by the baseline.

The model therefore cannot silently redefine the output contract.

## Ollama

The default local provider is a small HTTP adapter around Ollama.

Environment variables:

- TRACEBACK_MODEL — model name, default llama3.2
- OLLAMA_BASE_URL — Ollama URL, default http://127.0.0.1:11434
- TRACEBACK_OLLAMA_TIMEOUT — request timeout in seconds, default 60

The provider is isolated in app/providers/ollama.py. A different provider can implement the same LLMProvider protocol without changing domain or evaluation code.

## API

Send a request such as:

{
  "scenario_id": "database-pool-exhaustion",
  "mode": "llm",
  "model": "llama3.2"
}

Baseline mode remains the default and does not require a running model.

## Failure behavior

Malformed model JSON becomes a controlled diagnosis parsing error. Provider or network failures become an API 502 rather than a false successful investigation.

A model response is never treated as valid merely because it contains plausible prose.
