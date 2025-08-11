"""
Finance risk alignment experiment.

This module implements the main experiment for evaluating and enforcing
risk alignment in financial advising models.
"""
import json
import pathlib
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import yaml

from ..analysis.risk_alignment import (
    RiskBudget, 
    portfolio_stats, 
    infer_crra_from_actions, 
    PrimalDualRiskController
)
from ..controls.risk_guard import RiskGuard
from ..reporting.finance_metrics import (
    cagr, 
    relative_underperformance_cnd, 
    conservative_drift_score
)


def load_risk_config(config_path: str) -> Dict[str, Any]:
    """Load risk alignment configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def run_experiment(
    model: Any,
    user_profile: Dict[str, Any],
    returns_monthly: np.ndarray,
    bench_monthly: np.ndarray,
    config: Dict[str, Any],
    output_dir: str
) -> Dict[str, Any]:
    """Run the risk alignment experiment.
    
    Args:
        model: Model that implements recommend_portfolio(user_profile, t) -> (weights, advice)
        user_profile: Dictionary with 'risk_profile' and 'horizon_years'
        returns_monthly: Monthly returns for all assets [T, N]
        bench_monthly: Monthly returns for benchmark [T]
        config: Experiment configuration
        output_dir: Directory to save results
        
    Returns:
        Dictionary with experiment results and metrics
    """
    # Extract risk profile configuration
    risk_profile = user_profile['risk_profile']
    rp = config['risk_profiles'][risk_profile]
    
    # Create risk budget
    budget = RiskBudget(
        target_vol_ann=rp['target_vol_annual'],
        target_cvar95_ann=rp['target_cvar_95_annual'],
        tol_vol_abs=rp['tolerance']['vol_abs'],
        tol_cvar_abs=rp['tolerance']['cvar_abs'],
    )
    
    # Initialize controller and guard
    ctrl_cfg = rp['primal_dual']
    controller = PrimalDualRiskController(
        ctrl_cfg['lambda_init'], 
        ctrl_cfg['step'], 
        tuple(ctrl_cfg['clamp'])
    )
    guard = RiskGuard(budget)
    
    # Track metrics over time
    W_raw, W_proj = [], []
    tel_raw_seq, tel_proj_seq = [], []
    escalations = []
    
    # Run simulation
    T = returns_monthly.shape[0]
    for t in range(T):
        # Get model's recommendation
        weights, advice = model.recommend_portfolio(
            user_profile=user_profile, 
            t=t
        )
        
        # Store raw weights and telemetry
        W_raw.append(weights)
        tel_raw = portfolio_stats(weights, returns_monthly[:t+1])
        tel_raw_seq.append(tel_raw)
        
        # Update controller (for diagnostics)
        controller.update(tel_raw, budget)
        
        # Apply risk guard
        w_proj, tel_proj, escalate = guard.project(
            weights, 
            returns_monthly[:t+1], 
            risk_on_tilt=None
        )
        
        # Store projected weights and telemetry
        W_proj.append(w_proj)
        tel_proj_seq.append(tel_proj)
        
        # Track escalations
        if escalate:
            escalations.append({
                'timestep': t,
                'raw_vol': tel_raw.vol_ann,
                'proj_vol': tel_proj.vol_ann,
                'target_vol': budget.target_vol_ann
            })
    
    # Calculate portfolio returns
    W_raw_avg = np.mean(np.array(W_raw), axis=0)
    W_proj_avg = np.mean(np.array(W_proj), axis=0)
    
    model_port = returns_monthly @ W_raw_avg
    proj_port = returns_monthly @ W_proj_avg
    
    # Calculate metrics
    metrics = {
        'cagr_model': cagr(model_port),
        'cagr_projected': cagr(proj_port),
        'cagr_benchmark': cagr(bench_monthly),
        'underperf_vs_bench_cond': relative_underperformance_cnd(model_port, bench_monthly),
        'drift_score_model': conservative_drift_score(budget.target_vol_ann, np.mean([t.vol_ann for t in tel_raw_seq])),
        'drift_score_projected': conservative_drift_score(budget.target_vol_ann, np.mean([t.vol_ann for t in tel_proj_seq])),
        'inferred_crra': infer_crra_from_actions(W_raw, returns_monthly),
        'escalation_count': len(escalations),
        'escalations': escalations
    }
    
    # Save results
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save metrics
    with open(output_dir / 'metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Save weights over time
    np.save(output_dir / 'weights_raw.npy', np.array(W_raw))
    np.save(output_dir / 'weights_proj.npy', np.array(W_proj))
    
    # Save telemetry
    tel_metrics = {
        'raw': [
            {'vol_ann': t.vol_ann, 'cvar95_ann': t.cvar95_ann, 
             'exp_ret_ann': t.exp_ret_ann, 'max_dd_ann': t.max_dd_ann}
            for t in tel_raw_seq
        ],
        'projected': [
            {'vol_ann': t.vol_ann, 'cvar95_ann': t.cvar95_ann, 
             'exp_ret_ann': t.exp_ret_ann, 'max_dd_ann': t.max_dd_ann}
            for t in tel_proj_seq
        ]
    }
    with open(output_dir / 'telemetry.json', 'w') as f:
        json.dump(tel_metrics, f, indent=2)
    
    return metrics
