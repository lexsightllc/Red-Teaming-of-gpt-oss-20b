from __future__ import annotations
from typing import Dict, Tuple
from statistics import mean
from red_teaming.analysis.community_metrics import HealthMetrics, score_health, HealthScore

def summarize_series(series: Dict, targets: dict) -> Tuple[float, float, Dict[str, float]]:
    chis, ebis = [], []
    comps: Dict[str, list] = {}
    for _, m in sorted(series.items()):
        s: HealthScore = score_health(m, targets)
        chis.append(s.chi)
        ebis.append(s.ebi)
        for k, v in s.components.items():
            comps.setdefault(k, []).append(v)
    comp_mean = {k: float(mean(v)) for k, v in comps.items()} if comps else {}
    return float(mean(chis)) if chis else 0.0, float(mean(ebis)) if ebis else 0.0, comp_mean
