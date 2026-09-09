# Release

TraceBack publishes production container images to GitHub Container Registry (GHCR).

## Release flow

Create and push a semantic version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The release workflow then builds the production Docker image, publishes version metadata plus an immutable commit-SHA tag, and creates a GitHub artifact attestation for the exact pushed image digest.

Published image forms:

```text
ghcr.io/<owner>/<repository>:<version>
ghcr.io/<owner>/<repository>:sha-<commit>
```

The existing Docker Compose deployment remains the single-node deployment path. The application keeps durable SQLite state in the mounted `/data` volume and expects Ollama to remain an external provider.

## Build provenance

Released images are attested with GitHub artifact attestations. The attestation is bound to the exact OCI image digest produced by the release build, so consumers can verify that the image came from this repository and workflow rather than trusting a mutable tag alone.

Verify a published image with GitHub CLI:

```bash
gh attestation verify oci://ghcr.io/<owner>/<repository>:<version> -R <owner>/<repository>
```

The attestation establishes build provenance; it does not by itself prove that the image contains no vulnerabilities. The container-security workflow remains the vulnerability gate.

## Security boundary

The workflow grants only `contents: read` and `packages: write`. No long-lived registry credentials are required; GitHub's short-lived workflow token is used for publishing.

## Versioning

Use semantic version tags such as `v0.1.0`, `v0.2.0`, and `v1.0.0`.

Pull requests remain validation-only. Production publication happens only from explicit version tags or a manually dispatched release workflow.
