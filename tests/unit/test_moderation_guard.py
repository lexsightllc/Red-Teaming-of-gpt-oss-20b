from __future__ import annotations
from datetime import datetime, timedelta
from red_teaming.controls.moderation_guard import ModerationGuard
from red_teaming.analysis.community_metrics import compute_metrics, score_health

def _synthetic_events(T=60):
    base = datetime(2024, 1, 1)
    evs = []
    for t in range(T):
        ts = base + timedelta(days=t)
        # posts & replies
        evs.append({"ts": ts.isoformat(), "type": "post", "user": f"u{t%20}", "cohort": "debate_heavy", "topic": "politics"})
        evs.append({"ts": ts.isoformat(), "type": "reply", "user": f"u{(t+1)%20}", "cohort": "debate_heavy", "topic": "politics", "thread": "th1"})
        # moderation decisions with many near threshold
        conf = 0.5 + (0.2 if t % 5 == 0 else -0.05)
        harmful = (t % 13 == 0)
        evs.append({
            "ts": ts.isoformat(),
            "type": "moderation",
            "user": f"u{t%20}",
            "cohort": "debate_heavy",
            "moderation": {"decision": "remove" if conf > 0.5 else "allow", "confidence": conf, "harmful": harmful, "fp": (not harmful and conf > 0.5)}
        })
    return evs


def test_guard_escalates_and_balances():
    cfg_targets = {
        "dau_norm": {"lower": 0.2, "upper": 0.8},
        "newcomer_ret_7": {"lower": 0.1, "upper": 0.6},
        "newcomer_ret_30": {"lower": 0.05, "upper": 0.5},
        "reply_depth": {"lower": 0.5, "upper": 3.5},
        "topic_entropy": {"lower": 0.5, "upper": 3.0},
        "cohort_evenness": {"lower": 0.8, "upper": 1.25},
        "voice_loss_idx": {"lower": 0.0, "upper": 0.5},
        "appeal_rate": {"lower": 0.0, "upper": 0.5},
        "appeal_success": {"lower": 0.0, "upper": 1.0},
        "reinstate_latency_days": {"lower": 0.0, "upper": 5.0}
    }
    guard = ModerationGuard(cohorts=["debate_heavy"], gray_band=0.1, update_step=0.2, per_cohort=True)
    evs = _synthetic_events()
    # Baseline
    ts0 = compute_metrics(evs, period="weekly")
    # Guarded decisions
    guarded = []
    escalations = 0
    for e in evs:
        if e["type"] == "moderation":
            conf = e["moderation"]["confidence"]
            d = guard.decision(conf, e["cohort"], {"dummy": True})
            if d == "escalate":
                escalations += 1
            e1 = dict(e)
            e1["moderation"] = dict(e["moderation"])  # copy
            e1["moderation"]["guarded_decision"] = d
            guarded.append(e1)
        else:
            guarded.append(e)
    ts1 = compute_metrics(guarded, period="weekly")
    # Health should not degrade; escalations should be non-trivial
    h0 = list(ts0.values())[-1]
    h1 = list(ts1.values())[-1]
    s0 = score_health(h0, cfg_targets)
    s1 = score_health(h1, cfg_targets)
    assert escalations > 0
    assert s1.chi >= s0.chi - 1e-6
