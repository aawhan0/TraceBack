# Contributing to Traceback

Thanks for taking an interest in Traceback.

Traceback is an engineering-focused project exploring LLM-based incident investigation, MCP tool use, structured outputs, and deterministic evaluation. Contributions that improve correctness, reliability, security, documentation, or developer experience are welcome.

## Before You Start

- Check existing issues and pull requests before starting substantial work.
- Keep pull requests focused on one change.
- Prefer small, reviewable changes over broad refactors.
- Do not add infrastructure unless it solves a concrete project problem.
- Do not include secrets, credentials, private data, or generated build artifacts.
- If a change affects evaluation semantics, document the intended behavior and add tests.

## Development

Use the setup instructions in [README.md](README.md).

The project is being built incrementally, so avoid assuming that planned directories or commands already exist. Update the documentation when the actual development workflow becomes established.

## Verification

Before opening a pull request, run the checks relevant to the change.

At minimum, Python changes should eventually be covered by:

- Ruff/static analysis
- Python compilation
- Pytest

Changes to evaluation logic should include deterministic tests for:

- expected matches
- expected failures
- boundary conditions
- invalid model output where applicable

Changes to MCP tools should test both successful and failure behavior.

## Pull Requests

Please include:

1. **What changed**
2. **Why it changed**
3. **How it was verified**
4. **Any evaluation impact**

If the change modifies a metric, scenario definition, diagnosis schema, or evaluation rule, explicitly call that out. Evaluation changes can alter reported model performance and therefore deserve extra scrutiny.

Pull requests should pass the required GitHub Actions checks before merging.

## Code Style

Prefer:

- small functions
- explicit data models
- clear names
- typed interfaces
- deterministic behavior where possible
- focused modules
- tests around meaningful behavior

Avoid unrelated refactors in feature or bug-fix pull requests.

## Adding Scenarios

New incident scenarios should represent a meaningful production-like failure mode.

A scenario should have:

- a clear incident description
- realistic evidence
- deterministic ground truth
- an expected root cause
- root-cause matching criteria
- required evidence where appropriate
- tests for its evaluation behavior

Do not add scenarios solely to increase the scenario count.

## Evaluation Changes

Evaluation is a core feature of Traceback.

When changing an evaluation metric:

- define exactly what the metric measures
- keep the calculation deterministic
- add unit tests
- consider how the change affects historical comparisons
- avoid changing acceptance criteria merely to improve model scores

The evaluator should measure model behavior, not make the model appear better.

## Security-Sensitive Changes

For security-sensitive changes, explain the security impact without publishing exploit details in the pull request.

Do not commit:

- API keys
- tokens
- passwords
- private credentials
- sensitive incident data

## Documentation

Update documentation when public behavior, APIs, evaluation semantics, setup, or architecture changes.

Keep documentation factual. Planned functionality should be described as planned rather than presented as already implemented.

## Questions

If you are unsure about an implementation detail, open an issue or discussion before making a large change.
