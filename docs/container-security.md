# Container security

TraceBack treats the production container as a release artifact, not only a packaging convenience.

## CI boundary

The container security workflow:

1. builds the same production Dockerfile used for releases;
2. scans the resulting image for high and critical vulnerabilities;
3. ignores unfixed findings so the gate does not claim false precision;
4. generates an SPDX software bill of materials (SBOM);
5. uploads the SBOM as a workflow artifact.

Pull requests touching the production image or its runtime dependencies run the same checks before merge. Semantic-version release tags run the security workflow as well.

## Failure policy

A high or critical vulnerability with a known fix fails the image-security job. This keeps release quality tied to an explicit, reviewable policy instead of relying on manual inspection.

The workflow is intentionally independent of the application telemetry stack. It protects the image boundary without adding runtime dependencies to TraceBack.

## Current scope

This is a single-node deployment security gate. It does not claim to replace a full organizational container-security program, registry policy, runtime admission controller, or dependency-management service.

The SBOM is retained as a build artifact so a released image can be inspected later without rebuilding the application.
