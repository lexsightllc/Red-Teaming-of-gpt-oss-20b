from __future__ import annotations
import ast, json
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from red_teaming.analysis.code_metrics import measure_module, ModuleMetrics, FunctionMetrics

@dataclass
class QualityBudget:
    sloc_max: int
    fn_length_max: int
    avg_fn_length_max: int
    cyclomatic_per_fn_max: int
    cyclomatic_module_max: int
    nesting_depth_max: int
    duplication_pct_max: float
    import_count_max: int
    docstring_coverage_min: float
    mi_min: int

def _unused_imports(source: str) -> List[Tuple[int, str]]:
    tree = ast.parse(source)
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Store)}
    unused: List[Tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                if name not in used:
                    unused.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                if name not in used:
                    mod = node.module or ""
                    nm = f"{mod}.{alias.name}" if mod else alias.name
                    unused.append((node.lineno, nm))
    return unused

def _apply_simple_autofixes(source: str) -> str:
    try:
        lines = source.splitlines()
        unused = {(ln, nm) for (ln, nm) in _unused_imports(source)}
        kill_lines = {ln for (ln, _) in unused}
        new_lines = [ln for i, ln in enumerate(lines, start=1) if i not in kill_lines]
        return "\n".join(new_lines)
    except Exception:
        return source

def evaluate(source: str, budget: QualityBudget) -> Dict[str, Any]:
    m: ModuleMetrics = measure_module(source)
    violations: List[Dict[str, Any]] = []

    if m.sloc > budget.sloc_max:
        violations.append({"kind": "sloc_max", "value": m.sloc, "budget": budget.sloc_max, "remedy": "split module"})
    if m.imports > budget.import_count_max:
        violations.append({"kind": "import_count_max", "value": m.imports, "budget": budget.import_count_max, "remedy": "prune dependencies"})
    if m.duplication_pct > budget.duplication_pct_max:
        violations.append({"kind": "duplication_pct_max", "value": m.duplication_pct, "budget": budget.duplication_pct_max, "remedy": "extract common helper"})
    if m.cyclomatic_total > budget.cyclomatic_module_max:
        violations.append({"kind": "cyclomatic_module_max", "value": m.cyclomatic_total, "budget": budget.cyclomatic_module_max, "remedy": "decompose control flow"})
    if m.avg_fn_length > budget.avg_fn_length_max:
        violations.append({"kind": "avg_fn_length_max", "value": m.avg_fn_length, "budget": budget.avg_fn_length_max, "remedy": "extract functions"})
    if m.docstring_coverage < budget.docstring_coverage_min:
        violations.append({"kind": "docstring_coverage_min", "value": m.docstring_coverage, "budget": budget.docstring_coverage_min, "remedy": "document public API"})
    if m.mi_proxy < budget.mi_min:
        violations.append({"kind": "mi_min", "value": m.mi_proxy, "budget": budget.mi_min, "remedy": "simplify branching; reduce size"})

    for f in m.functions:
        if f.sloc > budget.fn_length_max:
            violations.append({"kind": "fn_length_max", "function": f.name, "value": f.sloc, "budget": budget.fn_length_max, "remedy": "extract helper"})
        if f.cyclomatic > budget.cyclomatic_per_fn_max:
            violations.append({"kind": "cyclomatic_per_fn_max", "function": f.name, "value": f.cyclomatic, "budget": budget.cyclomatic_per_fn_max, "remedy": "guard clauses; early returns"})
        if f.max_nesting > budget.nesting_depth_max:
            violations.append({"kind": "nesting_depth_max", "function": f.name, "value": f.max_nesting, "budget": budget.nesting_depth_max, "remedy": "flatten with guards or lookup table"})

    refactor_plan = {
        "summary": "complexity guard refactor plan",
        "actions": [
            {"when": "duplication_pct_max", "do": "extract_common_helpers"},
            {"when": "cyclomatic_per_fn_max", "do": "introduce_guard_clauses"},
            {"when": "nesting_depth_max", "do": "replace_if_chain_with_dispatch"},
            {"when": "import_count_max", "do": "remove_unused_imports"},
        ],
        "candidates": [v for v in violations if "function" in v]
    }

    status = "pass" if not violations else "fail"
    return {
        "status": status,
        "metrics": m.__dict__,
        "violations": violations,
        "refactor_plan": refactor_plan,
        "autofix_suggestion": _apply_simple_autofixes(source) if violations else None
    }
