# TraceBack Frontend Tour

The TraceBack dashboard is organized around the investigation lifecycle.

## 1. Dashboard

Use the dashboard for a quick view of recent investigation activity, current run outcomes, and entry points into the main workflows.

## 2. Playground

Start an investigation by selecting a scenario and execution mode. The workspace exposes the investigation flow, diagnosis, confidence, recommended action, and supporting evidence.

## 3. History

History contains persisted investigation runs. Open a run to inspect its complete detail workspace, including diagnosis metadata, status, and evidence usage.

## 4. Evaluation

Evaluation exposes the evaluator dimensions behind a run: root-cause match, evidence recall, evidence precision, confidence validity, and recommended-action presence. Re-run an investigation from the selected run to compare outcomes over time.

## 5. Experiments and Compare

Use Experiments for benchmark-oriented results and Compare for inspecting baseline-versus-LLM behavior across the same scenario set.

## 6. Reports

Reports provide a presentation-friendly view of investigation and benchmark results for sharing or review.

## 7. Supporting workspaces

- **Knowledge:** inspect the evidence and knowledge available to investigations.
- **Scenarios:** review the scenario definitions used by the evaluator.
- **Documentation:** understand the product and API concepts.
- **Settings:** manage frontend preferences and configuration.

## Recommended demo path

For a concise portfolio walkthrough, open **Playground → History → Evaluation → Compare**. This demonstrates the full path from running an investigation to reviewing persistence, measurable quality, and model-mode differences.