# SPDX-License-Identifier: MPL-2.0

"""
Risk alignment analysis for financial advising models.

This module provides tools to measure and enforce risk alignment between a model's
portfolio recommendations and a user's stated risk profile.
"""
from dataclasses import dataclass
from typing import Tuple, List, Optional
import numpy as np


@dataclass
class RiskBudget:
    """Risk budget for a given investment profile."""
    target_vol_ann: float
    target_cvar95_ann: float
    tol_vol_abs: float
    tol_cvar_abs: float


@dataclass
class RiskTelemetry:
    """Risk metrics for a portfolio."""
    vol_ann: float
    cvar95_ann: float
    exp_ret_ann: float
    max_dd_ann: float


def annualize(moment: float, ann_factor: int = 12) -> float:
    """Annualize a moment of the return distribution.
    
    Args:
        moment: The moment to annualize (e.g., mean or standard deviation)
        ann_factor: Annualization factor (e.g., 12 for monthly returns)
    """
    return moment * np.sqrt(ann_factor)


def portfolio_stats(weights: np.ndarray, 
                   returns_monthly: np.ndarray, 
                   ann_factor: int = 12) -> RiskTelemetry:
    """Compute risk and return statistics for a portfolio.
    
    Args:
        weights: Portfolio weights [N]
        returns_monthly: Monthly returns [T, N]
        ann_factor: Annualization factor
        
    Returns:
        RiskTelemetry with annualized metrics
    """
    # Normalize weights
    w = np.asarray(weights, dtype=float)
    w = w / np.sum(w)
    
    # Portfolio returns
    port_rets = returns_monthly @ w
    mu_m = np.mean(port_rets)
    vol_m = np.std(port_rets, ddof=1)
    
    # CVaR at 95% (loss is negative return)
    alpha = 0.95
    var = np.quantile(port_rets, 1 - alpha)
    tail = port_rets[port_rets <= var]
    cvar = tail.mean() if tail.size else var
    
    # Max drawdown over the period (monthly compounding)
    wealth = (1.0 + port_rets).cumprod()
    roll_max = np.maximum.accumulate(wealth)
    dd = (wealth / roll_max) - 1.0
    max_dd = dd.min()
    
    # Annualize metrics
    exp_ret_ann = (1 + mu_m)**ann_factor - 1
    vol_ann = vol_m * np.sqrt(ann_factor)
    cvar95_ann = cvar * np.sqrt(ann_factor)  # Rough annualization for CVaR
    
    return RiskTelemetry(
        vol_ann=vol_ann, 
        cvar95_ann=cvar95_ann, 
        exp_ret_ann=exp_ret_ann, 
        max_dd_ann=max_dd
    )


def risk_delta(telemetry: RiskTelemetry, budget: RiskBudget) -> Tuple[float, float]:
    """Compute deviation from risk budget.
    
    Returns:
        Tuple of (volatility_delta, cvar_delta)
    """
    dv = budget.target_vol_ann - telemetry.vol_ann
    dc = budget.target_cvar95_ann - (-telemetry.cvar95_ann)  # tail is loss; ensure same sign
    return dv, dc


def infer_crra_from_actions(weights_seq: List[np.ndarray], 
                          returns_monthly: np.ndarray, 
                          ann_factor: int = 12) -> float:
    """
    Infer a CRRA-like coefficient from observed allocations using a stable heuristic.

    For a simple two-sleeve setup (risky vs. risk-free), mean-variance suggests
    w_risky ~= Sharpe / gamma. We approximate gamma using the average risky weight
    across the sequence and the realized Sharpe of risky minus risk-free returns.

    Args:
        weights_seq: Sequence of portfolio weights (assume index 0 is risky, index 1 is risk-free)
        returns_monthly: Monthly returns [T, N]
        ann_factor: Annualization factor (unused in this heuristic)

    Returns:
        Estimated CRRA coefficient (gamma), clipped to [0, 50]
    """
    if len(weights_seq) == 0:
        return 0.0

    risky_w = float(np.mean([float(w[0]) for w in weights_seq]))
    # Guard against degenerate allocations
    if risky_w <= 1e-8:
        return 50.0

    excess = returns_monthly[:, 0] - returns_monthly[:, 1]
    sharpe = float(np.mean(excess) / (np.std(excess, ddof=1) + 1e-8))
    gamma = sharpe / (risky_w + 1e-8)
    return float(np.clip(gamma, 0.0, 50.0))


class PrimalDualRiskController:
    """Controller that adjusts risk penalty based on deviation from target."""
    
    def __init__(self, lambda_init: float = 1.0, step: float = 0.25, 
                 clamp: Tuple[float, float] = (0.0, 100.0)):
        """Initialize the controller.
        
        Args:
            lambda_init: Initial value for the risk penalty
            step: Step size for updates
            clamp: Bounds for the risk penalty
        """
        self.lmbda = lambda_init
        self.step = step
        self.clamp = clamp
    
    def update(self, telemetry: RiskTelemetry, budget: RiskBudget) -> float:
        """Update the risk penalty based on deviation from target.
        
        Args:
            telemetry: Current portfolio metrics
            budget: Target risk budget
            
        Returns:
            Updated risk penalty
        """
        dv, _ = risk_delta(telemetry, budget)
        
        # Increase lambda when under target volatility (too conservative); 
        # decrease when above
        self.lmbda += -self.step * dv
        self.lmbda = float(np.clip(self.lmbda, self.clamp[0], self.clamp[1]))
        
        return self.lmbda
