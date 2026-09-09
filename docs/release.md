# Release

TraceBack publishes production container images to GitHub Container Registry (GHCR).

## Release flow

Create and push a semantic version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The release workflow then builds the production Docker image and publishes version metadata plus an immutable commit-SHA tag.

Published image forms:

```text
ghcr.io/<owner>/<repository>:<version>
ghcr.io/<owner>/<repository>:sha-<commit>
```

The existing Docker Compose deployment remains the single-node deployment path. The application keeps durable SQLite state in the mounted `/data` volume and expects Ollama to remain an external provider.

## Security boundary

The workflow grants only `contents: read` and `packages: write`. No long-lived registry credentials are required; GitHub's short-lived workflow token is used for publishing.

## Versioning

Use semantic version tags such as `v0.1.0`, `v0.2.0`, and `v1.0.0`.

Pull requests remain validation-only. Production publication happens only from explicit version tags or a manually dispatched release workflow.
