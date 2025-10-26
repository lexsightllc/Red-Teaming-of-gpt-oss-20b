"""Command line interface glue for the red_teaming package."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path
import tempfile
from typing import Iterable, List, Sequence

import yaml


def _ensure_scoring_rubric(argv: List[str]) -> None:
    """Infer the scoring rubric path when only a config directory is supplied."""
    if "--scoring_rubric" in argv or "--config" not in argv:
        return

    cfg_idx = argv.index("--config")
    if cfg_idx + 1 >= len(argv):
        return

    config_path = Path(argv[cfg_idx + 1])
    candidate = config_path.parent / "scoring_rubric.yaml"
    if candidate.exists():
        argv.extend(["--scoring_rubric", str(candidate)])


def _synthesize_scenario_design(argv: List[str]) -> None:
    """Backfill scenario_design when provided config files use legacy keys."""
    if "--config" not in argv:
        return

    cfg_idx = argv.index("--config")
    if cfg_idx + 1 >= len(argv):
        return

    config_path = Path(argv[cfg_idx + 1])
    if not config_path.exists():
        return

    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if "scenario_design" in data:
        return

    scenario_design = {
        "generation_config": data.get("scenario_generation", {}),
        "complexity_config": data.get("scenario_complexity", {}),
        "preference_drift_config": data.get("preference_drift", {}),
        "trigger_variants_config": data.get("minimal_trigger_variants", {}),
    }
    data["scenario_design"] = scenario_design

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".yaml",
        prefix="merged_",
        dir=str(config_path.parent),
        delete=False,
    ) as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
        merged = Path(handle.name)

    argv[cfg_idx + 1] = str(merged)


def _prepare_argv(argv: Sequence[str]) -> List[str]:
    mutated = list(argv)
    _ensure_scoring_rubric(mutated)
    _synthesize_scenario_design(mutated)
    return mutated


def main(argv: Iterable[str] | None = None) -> None:
    """Entry point used by both ``python -m`` and ``scripts/dev`` workflows."""
    original_argv = list(argv if argv is not None else sys.argv[1:])
    prepared = _prepare_argv(original_argv)
    sys.argv = [sys.argv[0], *prepared]
    # Delegate to the historical entry-point to minimise behavioural drift.
    runpy.run_module("red_teaming.main", run_name="__main__")


if __name__ == "__main__":
    main()
