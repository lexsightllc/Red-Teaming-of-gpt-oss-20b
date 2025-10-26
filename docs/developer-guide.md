<!-- SPDX-License-Identifier: MPL-2.0 -->

# Developer Guide

## Prerequisites
- Python 3.11 (managed via `.tool-versions`)
- Node.js 20 for commitlint tooling
- Docker (optional) for reproducible containers

## Getting Started
1. Clone the repository.
2. Run `make bootstrap` to create the virtual environment, install dependencies, and configure hooks.
3. Use `make dev` to watch and rerun the CLI when source files change.
4. Run `make check` prior to submitting changes.

## Directory Layout
- `src/red_teaming/` — Primary Python package.
- `configs/` — YAML configuration sets for experiments.
- `docs/` — MkDocs site with ADRs, developer references, and diagrams.
- `scripts/` — Toolbelt wrappers for local automation (mirrored in PowerShell).
- `ci/` — Workflow helpers for GitHub Actions.
- `infra/` — Container build definitions and deployment manifests.
- `tests/` — Automated suites grouped by scope (unit, integration, e2e).

## Testing Strategy
- Unit tests exercise deterministic modules with synthetic fixtures.
- Integration tests execute pipeline slices with config-driven inputs.
- E2E tests describe Given/When/Then flows for user-visible behaviour.
- Coverage gates enforce 85% branch coverage; failing to meet the threshold will exit non-zero.

## Observability
Structured logging is enabled through Loguru. Each experiment seeds RNG sources, emits metrics via `red_teaming.reporting`, and publishes summaries suitable for dashboards. Extend instrumentation via `red_teaming.reporting.metrics` and `red_teaming.reproducibility.logging_redaction`.
