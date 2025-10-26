# SPDX-License-Identifier: MPL-2.0

"""
Risk guard for enforcing risk alignment in portfolio recommendations.

This module provides a RiskGuard class that projects proposed portfolios onto
the target risk surface defined by the user's risk profile.
"""
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
from ..analysis.risk_alignment import RiskBudget, portfolio_stats, RiskTelemetry


class RiskGuard:
    """Ensures portfolio recommendations align with target risk profile."""
    
    def __init__(self, budget: RiskBudget, ann_factor: int = 12, 
                 min_weight: float = -0.10, max_weight: float = 1.0):
        """Initialize the risk guard.
        
        Args:
            budget: Risk budget specifying target risk levels
            ann_factor: Annualization factor
            min_weight: Minimum allowed weight for any asset
            max_weight: Maximum allowed weight for any asset
        """
        self.budget = budget
        self.ann_factor = ann_factor
        self.min_weight = min_weight
        self.max_weight = max_weight
    
    def project(self, 
               weights: np.ndarray, 
               returns_monthly: np.ndarray, 
               risk_on_tilt: Optional[np.ndarray] = None) -> Tuple[np.ndarray, RiskTelemetry, bool]:
        """Project proposed weights onto the target risk surface.
        
        Args:
            weights: Proposed portfolio weights [N]
            returns_monthly: Historical monthly returns [T, N]
            risk_on_tilt: Optional vector that allocates marginal risk to growth assets
            
        Returns:
            Tuple of (projected_weights, telemetry, needs_escalation)
        """
        # Normalize input weights
        w = np.asarray(weights, dtype=float)
        w = w / np.sum(w)
        
        # Get current portfolio metrics
        tel = portfolio_stats(w, returns_monthly, ann_factor=self.ann_factor)
        vol_gap = self.budget.target_vol_ann - tel.vol_ann
        
        # If within tolerance, return as-is
        if abs(vol_gap) <= self.budget.tol_vol_abs:
            w_clipped = np.clip(w, self.min_weight, self.max_weight)
            w_normalized = w_clipped / np.sum(w_clipped)
            return w_normalized, tel, False
        
        # Scale weights toward target volatility
        scale = self.budget.target_vol_ann / (tel.vol_ann + 1e-8)
        w_scaled = w * scale
        
        # Optional tilt to allocate marginal risk into growth sleeve when under-risked
        if vol_gap > 0 and risk_on_tilt is not None:
            tilt = np.asarray(risk_on_tilt, dtype=float)
            tilt = tilt / (np.sum(np.abs(tilt)) + 1e-12)
            
            # Mix a portion of tilt proportional to remaining gap
            mix = np.clip(vol_gap / max(self.budget.target_vol_ann, 1e-8), 0.0, 0.25)
            w_scaled = (1 - mix) * w_scaled + mix * tilt
        
        # Clip and normalize
        w_proj = np.clip(w_scaled, self.min_weight, self.max_weight)
        w_proj = w_proj / np.sum(w_proj)
        
        # Get projected metrics
        tel_proj = portfolio_stats(w_proj, returns_monthly, ann_factor=self.ann_factor)
        
        # Check if still under target after projection
        under_vol = (self.budget.target_vol_ann - tel_proj.vol_ann) > self.budget.tol_vol_abs
        
        return w_proj, tel_proj, under_vol
