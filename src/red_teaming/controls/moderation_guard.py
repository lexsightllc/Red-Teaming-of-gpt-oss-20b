# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from red_teaming.analysis.community_metrics import HealthScore

@dataclass
class Thresholds:
    global_tau: float = 0.5
    cohort_tau: Dict[str, float] = field(default_factory=dict)

@dataclass
class GuardState:
    fp_multiplier: float = 1.0
    voice_multiplier: float = 1.0
    harm_multiplier: float = 1.0

class ModerationGuard:
    def __init__(self, cohorts: list[str], gray_band: float = 0.1, update_step: float = 0.15, per_cohort: bool = True):
        self.thr = Thresholds(global_tau=0.5, cohort_tau={c: 0.5 for c in cohorts})
        self.gray_band = gray_band
        self.step = update_step
        self.state = GuardState()
        self.per_cohort = per_cohort

    def decision(self, score: float, cohort: str, card: dict) -> str:
        tau = self.thr.cohort_tau.get(cohort, self.thr.global_tau) if self.per_cohort else self.thr.global_tau
        if abs(score - tau) <= self.gray_band:
            return "escalate"
        return "remove" if score >= tau else "allow"

    def update_from_health(self, hs: HealthScore):
        delta = self.step * (hs.ebi)
        self.thr.global_tau = float(max(0.05, min(0.95, self.thr.global_tau + delta)))
        for c in self.thr.cohort_tau:
            self.thr.cohort_tau[c] = float(max(0.05, min(0.95, self.thr.cohort_tau[c] + delta)))

    def learn_from_appeal(self, cohort: str, overturned: bool, score: float):
        if overturned and score >= self.thr.cohort_tau.get(cohort, self.thr.global_tau):
            adj = self.step * (score - self.thr.cohort_tau.get(cohort, self.thr.global_tau))
            if self.per_cohort and cohort in self.thr.cohort_tau:
                self.thr.cohort_tau[cohort] = float(min(0.95, self.thr.cohort_tau[cohort] + adj))
            else:
                self.thr.global_tau = float(min(0.95, self.thr.global_tau + adj))
