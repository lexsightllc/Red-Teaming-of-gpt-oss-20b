#!/usr/bin/env python3
"""Enforce repository license policy using pip-licenses output."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_REPORT = REPO_ROOT / "reports" / "pip-licenses.json"
SUMMARY_PATH = REPO_ROOT / "reports" / "license-summary.json"
ALLOWLIST_PATH = REPO_ROOT / "configs" / "license-allowlist.yml"


def _normalise(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", value.upper())


def main() -> int:
    if not RAW_REPORT.exists():
        print(f"pip-licenses report missing at {RAW_REPORT}", file=sys.stderr)
        return 1

    if not ALLOWLIST_PATH.exists():
        print(f"Allowlist file missing at {ALLOWLIST_PATH}", file=sys.stderr)
        return 1

    allowlist_data = yaml.safe_load(ALLOWLIST_PATH.read_text()) or {}
    allowed = {_normalise(item) for item in allowlist_data.get("allowed", []) if item}

    records = json.loads(RAW_REPORT.read_text())
    violations = []

    for record in records:
        license_field = record.get("License", "")
        if not license_field:
            violations.append({"name": record.get("Name", "unknown"), "license": ""})
            continue

        normalised_tokens = {
            _normalise(token)
            for token in re.split(r"[,&/;]", license_field)
            if _normalise(token)
        }

        if not normalised_tokens or normalised_tokens.isdisjoint(allowed):
            violations.append(
                {
                    "name": record.get("Name", "unknown"),
                    "license": license_field,
                }
            )

    summary = {
        "total_packages": len(records),
        "violations": violations,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2))

    if violations:
        print("Disallowed licenses detected:", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation['name']}: {violation['license'] or 'Unspecified'}", file=sys.stderr)
        print(f"See {SUMMARY_PATH} for details.", file=sys.stderr)
        return 1

    print(f"License scan passed. Summary written to {SUMMARY_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
