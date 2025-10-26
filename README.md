# Red-Teaming of GPT-OSS-20B

A structured platform for analysing and hardening large-model behaviour. The repository now follows a canonical layout so contributors can bootstrap, lint, test, and release with a single command set on any machine.

## Architecture Overview
- **Python Package:** `src/red_teaming/` contains the experiment orchestration pipeline, analysis modules, reporting utilities, reproducibility tooling, and ethics safeguards.
- **Configurations:** `configs/model_vulnerability_analysis/` stores YAML bundles that parameterise scenarios, scoring rubrics, and experiment budgets.
- **Documentation:** `docs/` is powered by MkDocs with ADRs, developer guides, and generated references.
- **Automation:** `scripts/` implements a uniform toolbelt (with PowerShell mirrors) surfaced through `make` targets. CI runs `make check` on every push.
- **Quality Gates:** Ruff, Black, isort, mypy, pytest (unit/integration/e2e), coverage, Bandit, pip-audit, and CycloneDX SBOM generation.

A compatibility shim remains at `src/main.py` for legacy runners; new entry points use `python -m red_teaming.cli`.

## Getting Started
```bash
git clone https://github.com/your-org/red-teaming-of-gpt-oss-20b.git
cd red-teaming-of-gpt-oss-20b
make bootstrap
```

Bootstrap creates `.venv`, installs pinned dependencies, configures `pre-commit`, sets the Conventional Commit template, and provisions Commitizen hooks. Verify the environment with:

```bash
make check
```

## Developer Tasks
All automation lives under `scripts/` and is mirrored in `Makefile` targets.

| Task | Command | Description |
|------|---------|-------------|
| Bootstrap | `make bootstrap` | Create the virtual environment, install dependencies, configure hooks. |
| Dev loop | `make dev` | Run the CLI with file watching via `watchfiles` when available. |
| Lint | `make lint` | Ruff + Black + isort (`--fix` optional). |
| Format | `make fmt` | Apply canonical formatting across `src`, `tests`, and `scripts`. |
| Type check | `make typecheck` | mypy in strict mode. |
| Unit+integration tests | `make test` | Pytest suites with deterministic fixtures. |
| E2E tests | `make e2e` | Behavioural scenarios with Given/When/Then comments. |
| Coverage | `make coverage` | Pytest with coverage enforcement (85% floor). |
| Build | `make build` | Build sdist + wheel via `python -m build`. |
| Package | `make package` | Produce wheel artefacts only. |
| Release | `make release` | Drive semantic-release tagging and changelog updates. |
| Update dependencies | `make update-deps` | Regenerate pinned lockfiles using `pip-compile`. |
| Security scan | `make security-scan` | Run Bandit and pip-audit. |
| SBOM | `make sbom` | Emit CycloneDX JSON under `sbom/`. |
| Docs | `make gen-docs` | Build the MkDocs documentation site. |
| Migrate | `make migrate` | Placeholder for database migrations (currently none). |
| Clean | `make clean` | Remove caches, build artefacts, coverage reports. |
| Check | `make check` | Execute lint → typecheck → tests → coverage → security-scan. |

## Running Experiments
```bash
python -m red_teaming.cli --config configs/model_vulnerability_analysis/testing_params.yaml \
  --scoring_rubric configs/model_vulnerability_analysis/scoring_rubric.yaml
```

Specialised modes mirror previous behaviours:

- **Risk Alignment (finance):** `python -m red_teaming.cli --risk_alignment --risk_config configs/model_vulnerability_analysis/risk_alignment.yaml`
- **Code Quality Gate:** `python -m red_teaming.cli --run_quality_gate --quality_budget configs/model_vulnerability_analysis/quality_budget.yaml`
- **Moderation A/B:** `python -m red_teaming.cli --moderation_abtest --community_config configs/model_vulnerability_analysis/community_health.yaml`
- **Evaluation Awareness:** `python -m red_teaming.cli --eval_awareness --eval_config configs/model_vulnerability_analysis/eval_awareness.yaml`

Generated outputs live under `reports/`; logs and temp configs land beside the supplied configuration files.

## Testing Philosophy
- **Unit tests (`tests/unit`)** mirror module structure, rely on deterministic seeds, and avoid network/filesystem effects.
- **Integration tests (`tests/integration`)** exercise pipeline segments with the canonical configs.
- **E2E tests (`tests/e2e`)** describe user-facing behaviours using Given/When/Then comments.
- Fixtures reside in `tests/fixtures`; snapshots are stored as text.

## Continuous Delivery & Security
- GitHub Actions workflow (`.github/workflows/ci.yml`) caches dependencies and runs `make check` on Ubuntu with Python 3.11.
- SBOM artefacts and coverage reports are uploaded on every build.
- CODEOWNERS enforce reviews for configs and scripts. Conventional Commit hooks gate contributions.
- `scripts/security-scan` runs Bandit and pip-audit; supply-chain checks extend via CycloneDX and semantic-release signing.

## Documentation & ADRs
Run `make gen-docs` to build the MkDocs site. ADRs live under `docs/adr/` with Mermaid diagrams describing architectural choices. Project metadata is tracked in `project.yaml`.

## Compatibility Notes
- Legacy `src.main` imports are preserved through a shim but will eventually migrate to `red_teaming.cli`.
- If Node.js tooling is unavailable, disable commitlint hooks via `SKIP=commitizen` temporarily but restore before merging.

For questions or escalations email `red-team-platform@your-org.example`.
