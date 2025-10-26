# SPDX-License-Identifier: MPL-2.0

from __future__ import annotations
import math, statistics
from dataclasses import dataclass
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Iterable

@dataclass
class HealthMetrics:
    dau_norm: float
    newcomer_ret_7: float
    newcomer_ret_30: float
    reply_depth: float
    topic_entropy: float
    cohort_evenness: float
    voice_loss_idx: float
    appeal_rate: float
    appeal_success: float
    reinstate_latency_days: float
    harm_rate: float
    fp_rate: float

def _period_key(ts: datetime, period: str) -> datetime:
    if period == "daily":  return datetime(ts.year, ts.month, ts.day)
    if period == "weekly": return datetime.fromisocalendar(ts.isocalendar().year, ts.isocalendar().week, 1)
    raise ValueError("period must be daily or weekly")

def _entropy(freqs: Dict[str,int]) -> float:
    n = sum(freqs.values()) or 1
    return -sum((c/n) * math.log(c/n + 1e-12) for c in freqs.values())

def _evenness_ratio(rate_a: float, rate_b: float) -> float:
    if rate_b == 0 and rate_a == 0: return 1.0
    if rate_b == 0: return float("inf")
    return rate_a / rate_b

def compute_metrics(events: Iterable[dict], period: str = "weekly") -> Dict[datetime, HealthMetrics]:
    by_period: Dict[datetime, List[dict]] = defaultdict(list)
    for e in events:
        ts = e["ts"]
        ts_dt = ts if isinstance(ts, datetime) else datetime.fromisoformat(ts)
        by_period[_period_key(ts_dt, period)].append(e)

    user_last_active: Dict[str, datetime] = {}
    user_join: Dict[str, datetime] = {}

    out: Dict[datetime, HealthMetrics] = {}

    for p, evs in sorted(by_period.items()):
        users = set()
        posters = set()
        topics = Counter()
        enforcement_by_cohort: Counter = Counter()
        active_by_cohort: Counter = Counter()
        harmful, fp, mod_cnt = 0, 0, 0
        appeals, appeals_overturned, reinstate_latencies = 0, 0, []

        threads: Dict[str, int] = defaultdict(int)
        for e in evs:
            users.add(e["user"])
            if e["type"] == "join":
                user_join[e["user"]] = e["ts"] if isinstance(e["ts"], datetime) else datetime.fromisoformat(e["ts"])
            if e["type"] in ("post", "reply"):
                posters.add(e["user"])
                user_last_active[e["user"]] = e["ts"] if isinstance(e["ts"], datetime) else datetime.fromisoformat(e["ts"])
                topics[e.get("topic","other")] += 1
                if e["type"] == "reply":
                    tid = e.get("thread","t")
                    threads[tid] += 1
            if e["type"] == "moderation":
                mod_cnt += 1
                c = e.get("cohort","general")
                enforcement_by_cohort[c] += 1
                active_by_cohort[c] += 1
                md = e.get("moderation",{})
                harmful += 1 if md.get("harmful", False) else 0
                fp += 1 if md.get("fp", False) else 0
            if e["type"] == "appeal":
                appeals += 1
                ap = e["appeal"]
                if ap.get("outcome") == "overturned":
                    appeals_overturned += 1
                    reinstate_latencies.append(float(ap.get("latency_days", 0.0)))

        dau = len(posters)
        mau = max(len(users), 1)
        dau_norm = dau / mau

        p_end = p + (timedelta(days=7) if period == "weekly" else timedelta(days=1))
        new_7 = {u for u,t0 in user_join.items() if t0 >= p - timedelta(days=7) and t0 <= p_end}
        new_30 = {u for u,t0 in user_join.items() if t0 >= p - timedelta(days=30) and t0 <= p_end}
        newcomer_ret_7 = len(new_7 & posters) / max(len(new_7), 1)
        newcomer_ret_30 = len(new_30 & posters) / max(len(new_30), 1)

        reply_depth = statistics.mean(threads.values()) if threads else 0.0
        topic_entropy = _entropy(topics)

        if active_by_cohort:
            top2 = [c for c,_ in active_by_cohort.most_common(2)]
            if len(top2) == 2:
                r_a = enforcement_by_cohort[top2[0]] / max(active_by_cohort[top2[0]], 1)
                r_b = enforcement_by_cohort[top2[1]] / max(active_by_cohort[top2[1]], 1)
                cohort_evenness = _evenness_ratio(r_a, r_b)
            else:
                cohort_evenness = 1.0
        else:
            cohort_evenness = 1.0

        moderated_users = {e["user"] for e in evs if e["type"] == "moderation"}
        previously_active = {u for u,t in user_last_active.items() if t <= p}
        chilled = len((moderated_users & previously_active) - posters)
        voice_loss_idx = chilled / max(len(moderated_users), 1)

        appeal_rate = appeals / max(mod_cnt, 1)
        appeal_success = appeals_overturned / max(appeals, 1) if appeals else 0.0
        reinstate_latency_days = (sum(reinstate_latencies)/len(reinstate_latencies)) if reinstate_latencies else 0.0

        harm_rate = harmful / max(mod_cnt, 1)
        fp_rate = fp / max(mod_cnt, 1)

        out[p] = HealthMetrics(
            dau_norm=dau_norm, newcomer_ret_7=newcomer_ret_7, newcomer_ret_30=newcomer_ret_30,
            reply_depth=reply_depth, topic_entropy=topic_entropy, cohort_evenness=cohort_evenness,
            voice_loss_idx=voice_loss_idx, appeal_rate=appeal_rate, appeal_success=appeal_success,
            reinstate_latency_days=reinstate_latency_days, harm_rate=harm_rate, fp_rate=fp_rate
        )
    return out

@dataclass
class HealthScore:
    chi: float   # Community Health Index (higher is better)
    ebi: float   # Enforcement Balance Index (0 means balanced)
    components: Dict[str,float]

def score_health(h: HealthMetrics, targets: dict) -> HealthScore:
    def clamp_band(x, lower, upper):
        if lower < upper:
            if x < lower: return (x - lower) / max(upper - lower, 1e-6)
            if x > upper: return (upper - x) / max(upper - lower, 1e-6)
            return 1.0
        return 0.0
    comp: Dict[str,float] = {}
    comp["engagement"] = clamp_band(h.dau_norm, targets["dau_norm"]["lower"], targets["dau_norm"]["upper"])
    comp["newcomer"]  = 0.5*clamp_band(h.newcomer_ret_7, targets["newcomer_ret_7"]["lower"], targets["newcomer_ret_7"]["upper"]) + \
                        0.5*clamp_band(h.newcomer_ret_30, targets["newcomer_ret_30"]["lower"], targets["newcomer_ret_30"]["upper"])
    comp["discussion"] = clamp_band(h.reply_depth, targets["reply_depth"]["lower"], targets["reply_depth"]["upper"])
    comp["diversity"]  = clamp_band(h.topic_entropy, targets["topic_entropy"]["lower"], targets["topic_entropy"]["upper"])
    low, high = targets["cohort_evenness"]["lower"], targets["cohort_evenness"]["upper"]
    even = 1.0 if low <= h.cohort_evenness <= high else max(0.0, 1.0 - abs(math.log(max(h.cohort_evenness,1e-6))))
    comp["evenness"] = even
    comp["voice"]    = clamp_band(1.0 - h.voice_loss_idx, 1.0 - targets["voice_loss_idx"]["upper"], 1.0)
    comp["appeals"]  = 0.5*clamp_band(h.appeal_rate, targets["appeal_rate"]["lower"], targets["appeal_rate"]["upper"]) + \
                       0.5*clamp_band(h.appeal_success, targets["appeal_success"]["lower"], targets["appeal_success"]["upper"]) 
    comp["latency"]  = clamp_band(targets["reinstate_latency_days"]["upper"] - h.reinstate_latency_days, 0.0, targets["reinstate_latency_days"]["upper"])

    weights = {"engagement":0.2,"newcomer":0.15,"discussion":0.1,"diversity":0.15,"evenness":0.1,"voice":0.2,"appeals":0.05,"latency":0.05}
    chi = sum(weights[k]*comp[k] for k in weights)

    ebi = 0.0
    ebi += (targets["voice_loss_idx"]["upper"] - h.voice_loss_idx) * 1.0
    ebi += (h.appeal_success - targets["appeal_success"]["lower"]) * -0.5
    ebi += (h.fp_rate - 0.02) * -2.0
    ebi += (0.01 - h.harm_rate) * 2.0
    return HealthScore(chi=float(max(0.0, min(1.0, chi))), ebi=float(ebi), components=comp)
