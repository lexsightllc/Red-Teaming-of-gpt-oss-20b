from __future__ import annotations
import json, pathlib, yaml
from red_teaming.analysis.code_metrics import measure_module
from red_teaming.controls.complexity_guard import QualityBudget, evaluate
from red_teaming.reporting.code_debt_score import complexity_debt_units

def run(source_code: str, budget_cfg: str, outpath: str):
    cfg = yaml.safe_load(open(budget_cfg, "r"))
    b = cfg["defaults"]
    budget = QualityBudget(
        sloc_max=b["sloc_max"], fn_length_max=b["fn_length_max"], avg_fn_length_max=b["avg_fn_length_max"],
        cyclomatic_per_fn_max=b["cyclomatic_per_fn_max"], cyclomatic_module_max=b["cyclomatic_module_max"],
        nesting_depth_max=b["nesting_depth_max"], duplication_pct_max=b["duplication_pct_max"],
        import_count_max=b["import_count_max"], docstring_coverage_min=b["docstring_coverage_min"], mi_min=b["mi_min"]
    )
    res = evaluate(source_code, budget)
    metrics = measure_module(source_code)
    # Convert nested dataclasses to JSON-serializable dicts
    metrics_dict = dict(metrics.__dict__)
    metrics_dict["functions"] = [f.__dict__ for f in metrics.functions]
    report = {
        "status": res["status"],
        "metrics": metrics_dict,
        "violations": res["violations"],
        "debt_score": complexity_debt_units(metrics),
        "autofix_preview": res["autofix_suggestion"]
    }
    pathlib.Path(outpath).parent.mkdir(parents=True, exist_ok=True)
    open(outpath, "w").write(json.dumps(report, indent=2))
    return 0 if res["status"] == "pass" else 1
