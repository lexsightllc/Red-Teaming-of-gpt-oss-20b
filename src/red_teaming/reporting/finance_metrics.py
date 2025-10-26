"""
Finance-specific metrics for evaluating portfolio performance and risk alignment.
"""
from typing import Optional
import numpy as np


def cagr(returns_monthly: np.ndarray) -> float:
    """Calculate Compound Annual Growth Rate (CAGR) from monthly returns.
    
    Args:
        returns_monthly: Array of monthly returns
        
    Returns:
        Annualized return (CAGR) as a decimal
    """
    if len(returns_monthly) == 0:
        return 0.0
    
    # Calculate total return
    total_return = np.prod(1 + returns_monthly) - 1.0
    
    # Convert to annualized return
    years = len(returns_monthly) / 12.0
    return (1.0 + total_return) ** (1.0 / years) - 1.0


def relative_underperformance_cnd(model_rets: np.ndarray, 
                               bench_rets: np.ndarray, 
                               window: int = 12) -> float:
    """Measure relative underperformance conditioned on volatility regime.
    
    Compares model returns to benchmark returns in similar volatility regimes.
    
    Args:
        model_rets: Model's monthly returns
        bench_rets: Benchmark's monthly returns
        window: Rolling window size for volatility calculation
        
    Returns:
        Average underperformance in similar volatility regimes
    """
    if len(model_rets) != len(bench_rets):
        raise ValueError("Model and benchmark returns must have same length")
    
    if len(model_rets) < window + 1:
        return 0.0  # Not enough data
    
    def roll_vol(x: np.ndarray, w: int) -> np.ndarray:
        """Calculate rolling volatility."""
        result = np.full_like(x, np.nan)
        for i in range(w-1, len(x)):
            result[i] = np.std(x[i-w+1:i+1], ddof=1)
        return result
    
    # Calculate rolling volatilities
    mv = roll_vol(model_rets, window)
    bv = roll_vol(bench_rets, window)
    
    # Only compare periods where we have volatility data
    mask = ~np.isnan(mv) & ~np.isnan(bv)
    if not np.any(mask):
        return 0.0
    
    mv = mv[mask]
    bv = bv[mask]
    
    # Define volatility regimes using quantiles
    all_vol = np.concatenate([mv, bv])
    bins = np.quantile(all_vol, [0.33, 0.66])
    
    # Create masks for each regime
    mask_lo = (mv <= bins[0]) & (bv <= bins[0])
    mask_md = (mv > bins[0]) & (mv <= bins[1]) & (bv > bins[0]) & (bv <= bins[1])
    mask_hi = (mv > bins[1]) & (bv > bins[1])
    
    def avg(x: np.ndarray, m: np.ndarray) -> Optional[float]:
        """Helper to calculate average, returning None if no data."""
        if m.sum() == 0:
            return None
        return np.mean(x[m])
    
    # Calculate average underperformance in each regime
    d_lo = avg(bench_rets[mask] - model_rets[mask], mask_lo)
    d_md = avg(bench_rets[mask] - model_rets[mask], mask_md)
    d_hi = avg(bench_rets[mask] - model_rets[mask], mask_hi)
    
    # Average across non-None regimes
    diffs = [d for d in [d_lo, d_md, d_hi] if d is not None]
    return float(np.mean(diffs)) if diffs else 0.0


def conservative_drift_score(target_vol_ann: float, 
                           realized_vol_ann: float) -> float:
    """Calculate conservative drift score.
    
    Measures how much the realized volatility is below the target.
    
    Args:
        target_vol_ann: Target annualized volatility
        realized_vol_ann: Realized annualized volatility
        
    Returns:
        Positive when realized vol is below target, zero otherwise
    """
    # Round to mitigate floating-point artifacts in equality checks
    return round(max(0.0, target_vol_ann - realized_vol_ann), 8)
