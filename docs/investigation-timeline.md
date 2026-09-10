# Investigation Timeline

TraceBack records a structured execution timeline for each investigation. The timeline shows the major runtime phases without exposing prompts or internal model reasoning.

A timeline contains:

1. Investigation created
2. Investigation started
3. Investigator execution
4. Investigation completed or failed

Each entry includes its sequence, phase, duration, and relevant operational metadata. The timeline is intended to answer **what the system did and when**, while the diagnosis and evaluation explain **what it concluded and whether that conclusion passed**.

The timeline is deterministic runtime telemetry, not a transcript of hidden model reasoning.
