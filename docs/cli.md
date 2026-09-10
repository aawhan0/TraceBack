# TraceBack CLI

The `traceback` command is the terminal interface for running investigations and evaluating saved results without opening the web dashboard.

## Install

From the repository root, create the Python environment and install TraceBack in editable mode:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

The package registers the `traceback` executable automatically.

Check the available commands with:

```powershell
traceback --help
```

## 1. List incident scenarios

See the scenarios available in the version-controlled catalog:

```powershell
traceback scenarios
```

Each scenario has an ID and title. Use the ID with `investigate` or `benchmark`.

## 2. Run an investigation

Run the deterministic baseline for one scenario:

```powershell
traceback investigate database-pool-exhaustion
```

The command prints structured JSON containing the run ID, diagnosis, evaluation metrics, pass/fail status, provider and duration.

Use another scenario by replacing the scenario ID:

```powershell
traceback investigate redis-connectivity-failure
traceback investigate worker-cpu-saturation
```

### LLM mode

LLM mode uses the configured Ollama provider:

```powershell
traceback investigate database-pool-exhaustion --mode llm --model llama3.2
```

The deterministic baseline does not require an LLM runtime. LLM mode requires a reachable Ollama service and model.

## 3. Inspect persisted runs

List recent investigation runs:

```powershell
traceback runs
```

Filter by scenario and limit the result set:

```powershell
traceback runs --scenario-id database-pool-exhaustion --limit 10
```

Show one run by its run ID:

```powershell
traceback show <run-id>
```

View aggregate statistics:

```powershell
traceback stats
traceback stats --scenario-id database-pool-exhaustion
```

## 4. Run a benchmark

Run a repeatable baseline benchmark across the scenario catalog:

```powershell
traceback benchmark --mode baseline --repetitions 3 --name baseline-smoke
```

Limit the benchmark to selected scenarios by repeating `--scenario-id`:

```powershell
traceback benchmark --scenario-id database-pool-exhaustion --scenario-id redis-connectivity-failure --repetitions 3 --name database-redis-smoke
```

LLM benchmark:

```powershell
traceback benchmark --mode llm --model llama3.2 --repetitions 3 --name llama-smoke
```

The benchmark persists its experiment record, dataset identity, provenance and regression result.

### Regression gates

Set the minimum acceptable pass rate:

```powershell
traceback benchmark --repetitions 3 --min-pass-rate 0.9 --name baseline-gated
```

Make the CLI exit non-zero when the regression gate fails:

```powershell
traceback benchmark --repetitions 3 --min-pass-rate 0.9 --fail-on-regression
```

Generate a Markdown benchmark report instead of the default JSON output:

```powershell
traceback benchmark --repetitions 3 --name baseline-report --report
```

## 5. Inspect saved experiments

List persisted experiments:

```powershell
traceback experiments
traceback experiments --limit 50
```

Show one experiment:

```powershell
traceback experiment <experiment-id>
```

## 6. Compare experiments

Compare a baseline experiment with a candidate experiment using their persisted IDs:

```powershell
traceback compare <baseline-id> <candidate-id>
```

Render the comparison as Markdown:

```powershell
traceback compare <baseline-id> <candidate-id> --report
```

Comparisons use the persisted dataset identity, so experiments built from incompatible datasets are rejected instead of producing a misleading comparison.

## 7. Run a configuration matrix

A matrix evaluates multiple configurations against one immutable dataset.

Baseline only:

```powershell
traceback matrix --name model-matrix --config baseline=baseline --repetitions 3
```

Baseline versus an Ollama model:

```powershell
traceback matrix --name model-matrix --config baseline=baseline --config llama=llm:llama3.2 --repetitions 3
```

Add selected scenarios with repeated `--scenario-id` arguments:

```powershell
traceback matrix --name database-matrix --config baseline=baseline --config llama=llm:llama3.2 --scenario-id database-pool-exhaustion --repetitions 3
```

The result includes a matrix ID, dataset fingerprint, experiment IDs and the best experiment ID.

## Typical workflow

For a quick local investigation:

```text
traceback scenarios
        ↓
traceback investigate <scenario-id>
        ↓
traceback runs
        ↓
traceback show <run-id>
```

For evaluation work:

```text
benchmark baseline
        ↓
benchmark candidate
        ↓
compare baseline candidate
        ↓
inspect regression result
```

For model/configuration evaluation:

```text
matrix multiple configurations
        ↓
inspect experiment IDs
        ↓
compare persisted experiments
        ↓
identify regressions or improvements
```

## Configuration

LLM mode reads the same environment configuration used by the application:

- `TRACEBACK_MODEL` — default Ollama model.
- `OLLAMA_BASE_URL` — Ollama service URL.
- `TRACEBACK_OLLAMA_TIMEOUT` — Ollama request timeout.

The CLI also uses the configured SQLite database path, so investigation runs and experiments created from the CLI are available to the API/dashboard when they use the same database configuration.

## Help for any command

Every command exposes its own arguments and defaults through argparse:

```powershell
traceback investigate --help
traceback benchmark --help
traceback matrix --help
traceback runs --help
traceback experiments --help
traceback compare --help
```

For the web workflow, see the dashboard's Documentation page or the main [README](../README.md).
