from __future__ import annotations
import ast, math, re
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class FunctionMetrics:
    name: str
    sloc: int
    cyclomatic: int
    max_nesting: int
    has_docstring: bool

@dataclass
class ModuleMetrics:
    sloc: int
    imports: int
    duplication_pct: float
    functions: List[FunctionMetrics]
    cyclomatic_total: int
    avg_fn_length: float
    docstring_coverage: float
    mi_proxy: float

_CONTROL_NODES = (
    ast.If, ast.For, ast.While, ast.With, ast.Try, ast.BoolOp, ast.IfExp
)

def _sloc(source: str) -> int:
    lines = [ln for ln in source.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    return len(lines)

def _imports(tree: ast.AST) -> int:
    return sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))

def _cyclomatic(node: ast.AST) -> int:
    count = 1
    for n in ast.walk(node):
        if isinstance(n, ast.If): count += 1
        elif isinstance(n, (ast.For, ast.While)): count += 1
        elif isinstance(n, ast.BoolOp): count += len(n.values) - 1
        elif isinstance(n, ast.Try): count += len(n.handlers) + (1 if n.finalbody else 0)
        elif isinstance(n, ast.IfExp): count += 1
        elif isinstance(n, ast.comprehension): count += 1
    return count

def _max_nesting(node: ast.AST) -> int:
    max_depth = 0
    def visit(n, depth):
        nonlocal max_depth
        if isinstance(n, _CONTROL_NODES): depth += 1
        max_depth = max(max_depth, depth)
        for c in ast.iter_child_nodes(n): visit(c, depth)
    visit(node, 0)
    return max_depth

def _duplication_pct(source: str, k: int = 6) -> float:
    # Token-level w-shingle duplication ratio
    tokens = re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\S", source)
    if len(tokens) < k: return 0.0
    shingles = [" ".join(tokens[i:i+k]) for i in range(len(tokens)-k+1)]
    total = len(shingles)
    unique = len(set(shingles))
    return float(1.0 - unique / total)

def _maintainability_index_proxy(sloc: int, cyclomatic_total: int, token_count: int) -> float:
    # MI ≈ scaled inverse of ln(volume) and CC; crude but monotonic
    if sloc <= 0: return 100.0
    volume = max(token_count, 1)
    raw = 171 - 5.2 * math.log(volume) - 0.23 * cyclomatic_total - 16.2 * math.log(sloc)
    return max(0.0, min(100.0, 100 * raw / 171))

def _token_count(source: str) -> int:
    return len(re.findall(r"\S+", source))

def measure_module(source: str) -> ModuleMetrics:
    tree = ast.parse(source)
    sloc = _sloc(source)
    imports = _imports(tree)
    dup = _duplication_pct(source)
    fns: List[FunctionMetrics] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = getattr(node, "lineno", None)
            end = getattr(node, "end_lineno", None)
            fn_sloc = (end - start + 1) if (start and end) else 0
            fns.append(FunctionMetrics(
                name=node.name,
                sloc=fn_sloc,
                cyclomatic=_cyclomatic(node),
                max_nesting=_max_nesting(node),
                has_docstring=ast.get_docstring(node) is not None
            ))
    cc_total = sum(f.cyclomatic for f in fns)
    avg_len = (sum(f.sloc for f in fns) / len(fns)) if fns else 0.0
    pub_fns = [f for f in fns if not f.name.startswith("_")]
    doc_cov = (sum(1 for f in pub_fns if f.has_docstring) / len(pub_fns)) if pub_fns else 1.0
    mi = _maintainability_index_proxy(sloc, cc_total, _token_count(source))
    return ModuleMetrics(
        sloc=sloc, imports=imports, duplication_pct=dup, functions=fns,
        cyclomatic_total=cc_total, avg_fn_length=avg_len, docstring_coverage=doc_cov,
        mi_proxy=mi
    )
