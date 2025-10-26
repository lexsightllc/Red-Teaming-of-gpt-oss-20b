# SPDX-License-Identifier: MPL-2.0

"""
Tests for risk alignment functionality.
"""
import numpy as np
import pytest
from pathlib import Path

from red_teaming.analysis.risk_alignment import (
    RiskBudget, 
    portfolio_stats, 
    infer_crra_from_actions,
    PrimalDualRiskController
)
from red_teaming.controls.risk_guard import RiskGuard
from red_teaming.reporting.finance_metrics import (
    cagr,
    relative_underperformance_cnd,
    conservative_drift_score
)


def test_portfolio_stats_basic():
    """Test basic portfolio statistics calculation."""
    # Simple 2-asset case with perfect negative correlation
    returns = np.array([
        [0.1, -0.1],
        [0.1, -0.1],
        [0.1, -0.1],
    ])
    
    # Equal weights
    weights = np.array([0.5, 0.5])
    
    # Portfolio should have zero variance with perfect negative correlation
    stats = portfolio_stats(weights, returns, ann_factor=12)
    
    assert np.isclose(stats.vol_ann, 0.0, atol=1e-10)
    assert np.isclose(stats.exp_ret_ann, 0.0, atol=1e-10)


def test_risk_guard_projection():
    """Test that risk guard projects portfolios to target risk level."""
    # Create synthetic returns with known properties
    np.random.seed(42)
    T = 60  # 5 years of monthly data
    N = 3   # 3 assets
    
    # Asset 0: High risk/return, Asset 1: Medium, Asset 2: Low
    means = np.array([0.15/12, 0.10/12, 0.05/12])
    cov = np.array([
        [0.20**2/12, 0.1*0.2*0.15, 0.0],
        [0.1*0.2*0.15, 0.15**2/12, 0.0],
        [0.0, 0.0, 0.05**2/12]
    ])
    
    # Generate correlated returns
    returns = np.random.multivariate_normal(means, cov, size=T)
    
    # Create a conservative portfolio (mostly cash)
    conservative_weights = np.array([0.1, 0.2, 0.7])
    
    # Set up a moderate risk budget
    budget = RiskBudget(
        target_vol_ann=0.14,
        target_cvar95_ann=0.18,
        tol_vol_abs=0.01,
        tol_cvar_abs=0.02
    )
    
    # Create guard and project
    guard = RiskGuard(budget)
    w_proj, tel_proj, escalate = guard.project(conservative_weights, returns)
    
    # Check that projected portfolio is closer to target vol
    tel_orig = portfolio_stats(conservative_weights, returns)
    assert abs(tel_proj.vol_ann - budget.target_vol_ann) <= abs(tel_orig.vol_ann - budget.target_vol_ann)
    
    # Check weights are properly normalized
    assert np.isclose(np.sum(w_proj), 1.0, atol=1e-10)
    assert np.all(w_proj >= -0.1)  # Respect minimum weight
    assert np.all(w_proj <= 1.0)   # Respect maximum weight


def test_crra_inference():
    """Test that we can infer risk aversion from allocations."""
    # Create synthetic returns
    np.random.seed(123)
    T = 120  # 10 years of monthly data
    
    # Two assets: risky and risk-free
    returns = np.column_stack([
        0.01 + 0.1 * np.random.randn(T),  # Risky asset
        0.001 * np.ones(T)                # Risk-free
    ])
    
    # Create sequence of weights showing increasing risk aversion
    gammas = np.linspace(1, 10, 10)
    weights_seq = []
    
    for gamma in gammas:
        # Simple mean-variance weights
        excess_returns = returns[:, 0] - returns[:, 1]
        sharpe = np.mean(excess_returns) / np.std(excess_returns, ddof=1)
        w_risky = sharpe / gamma
        weights_seq.append(np.array([w_risky, 1 - w_risky]))
    
    # Infer CRRA coefficient
    inferred_gamma = infer_crra_from_actions(weights_seq, returns)
    
    # Should be close to the average gamma in the sequence
    assert 2.0 <= inferred_gamma <= 8.0


def test_conservative_drift_score():
    """Test that conservative drift is properly measured."""
    # No drift when at target
    assert conservative_drift_score(0.15, 0.15) == 0.0
    
    # Positive when below target
    assert conservative_drift_score(0.15, 0.10) == 0.05
    
    # Zero when above target
    assert conservative_drift_score(0.15, 0.20) == 0.0


def test_relative_underperformance():
    """Test conditional underperformance calculation."""
    # Create synthetic returns where benchmark outperforms in all regimes
    np.random.seed(42)
    T = 120
    
    # Model returns with different volatility regimes
    low_vol = 0.01 + 0.05 * np.random.randn(T//3)
    med_vol = 0.01 + 0.10 * np.random.randn(T//3)
    high_vol = 0.01 + 0.20 * np.random.randn(T//3 + T%3)
    model_rets = np.concatenate([low_vol, med_vol, high_vol])
    
    # Benchmark has same vol but higher returns
    bench_rets = model_rets + 0.01  # 1% higher return per period
    
    # Should detect underperformance
    underperf = relative_underperformance_cnd(model_rets, bench_rets)
    assert underperf > 0.005  # Should be close to 0.01
    
    # If we flip, should be negative (outperformance)
    underperf_inv = relative_underperformance_cnd(bench_rets, model_rets)
    assert underperf_inv < -0.005
