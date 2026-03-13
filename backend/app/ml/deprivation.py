"""
deprivation.py
Standalone deprivation cost functions for the Flood Relief MDP.

These functions were previously inlined in mdp.py.  Centralising them here
avoids circular imports and makes the economic model easy to unit-test and
replace independently.

Reference: Holguin-Veras et al. (2013) — exponential deprivation cost model.
"""

from __future__ import annotations

import math
import numpy as np
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.ml.mdp import DistrictState


# ── Core deprivation cost functions ───────────────────────────────────────────

def deprivation_cost(delta: int) -> float:
    """
    Cumulative deprivation cost after δ consecutive periods without supply.

    Formula:  γ(δ) = e^(0.065·δ) − 1
    γ(0) = 0 (no deprivation cost when fully supplied).

    Parameters
    ----------
    delta : int
        Number of periods the district has been in deprivation.

    Returns
    -------
    float
        Non-negative deprivation cost value.
    """
    return math.exp(0.065 * delta) - 1.0


def marginal_deprivation_cost(delta: int) -> float:
    """
    Marginal (incremental) deprivation cost for the transition δ → δ+1.

    Formula:  g(δ) = max(0, γ(δ) − γ(δ−1))

    Parameters
    ----------
    delta : int
        Current deprivation period count.

    Returns
    -------
    float
        Non-negative marginal cost (0 when delta ≤ 0).
    """
    return max(0.0, deprivation_cost(delta) - deprivation_cost(delta - 1))


def expected_deprivation_cost(
    inv_x:       float,
    delta:       int,
    demand_est:  float,
    demand_std:  float,
) -> float:
    """
    Expected deprivation cost feature for Value Function Approximation (VFA).

    Computes a conservative estimate of next-period deprivation cost given
    post-decision inventory *inv_x*, using a cautious (mean + 2σ) demand
    scenario to capture risk.

    Formula: G^x = g(δ+1) × max(0, d_cautious − inv_x)

    Parameters
    ----------
    inv_x      : Post-decision inventory at a district (units).
    delta      : Current deprivation period counter.
    demand_est : Expected demand for the next period.
    demand_std : Standard deviation of demand.

    Returns
    -------
    float
        Estimated expected deprivation cost contribution.
    """
    cautious_demand = demand_est + 2.0 * demand_std
    shortage = max(0.0, cautious_demand - inv_x)
    return marginal_deprivation_cost(delta + 1) * shortage


# ── Aggregate helpers ──────────────────────────────────────────────────────────

def total_episode_deprivation_cost(districts: "List[DistrictState]") -> float:
    """
    Sum of marginal deprivation cost × shortage across all districts.

    Useful as a single-step aggregate deprivation signal during simulation.

    Parameters
    ----------
    districts : list of DistrictState
        Current district states within the MDP.

    Returns
    -------
    float
        Total deprivation cost for this time step.
    """
    return sum(
        marginal_deprivation_cost(d.deprivation_time) * d.shortage
        for d in districts
    )


def deprivation_risk_score(district: "DistrictState", horizon: int = 5) -> float:
    """
    Estimated cumulative deprivation cost over the next *horizon* periods
    assuming NO resupply and constant mean demand.

    This is a planning metric, not used directly in the MDP transition.

    Parameters
    ----------
    district : DistrictState
        The district whose risk we are scoring.
    horizon  : int
        Number of future periods to simulate (default 5).

    Returns
    -------
    float
        Estimated cumulative deprivation cost if the district receives no
        relief over the next *horizon* periods.
    """
    inv   = district.inventory
    delta = district.deprivation_time
    total = 0.0

    for _ in range(horizon):
        demand = district.demand_estimate
        if inv < demand:
            delta += 1
            inv    = 0.0
        else:
            inv   -= demand
            delta  = 0
        total += marginal_deprivation_cost(delta) * max(0.0, demand - inv)

    return total
