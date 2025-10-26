<!-- SPDX-License-Identifier: MPL-2.0 -->

# Continuous Integration

The GitHub Actions workflow defined in `.github/workflows/ci.yml` executes `make check` across Python 3.11 on Ubuntu. Dependency caching uses pip's built-in cache keyed by the requirements lockfiles.

Quality gates:
- Lint: Ruff, Black, isort
- Type checking: mypy (strict)
- Tests: unit + integration + e2e with coverage enforcement
- Security: Bandit and pip-audit
- SBOM: CycloneDX JSON published as artifact
