"""
equity.py
Fairness / equity metrics for flood-relief allocation.

Pure math helpers — no dependencies on any other ReliefNet module so that
unit tests can import them in isolation.

Research Basis
--------------
Improvement 1 from research_improvements.md:
    "Balancing Efficiency and Equity in Post-Flood Relief Allocation
     using Constrained Proximal Policy Optimization"

The Gini coefficient is the standard tool from welfare economics for
measuring inequality in a distribution.  Max-Min fairness penalises the
absolute worst-served district.
"""

from __future__ import annotations

import math
from typing import List


# ── Core Equity Metrics ───────────────────────────────────────────────────────

def gini_coefficient(values: List[float]) -> float:
    """
    Compute the Gini coefficient of a non-negative distribution.

    Gini = 0  →  perfect equality (all districts equally served).
    Gini = 1  →  maximum inequality (all shortage in one district).

    Parameters
    ----------
    values : list of float
        Per-district shortage values (≥ 0).

    Returns
    -------
    float in [0, 1].
    """
    n = len(values)
    if n == 0:
        return 0.0
    sorted_v = sorted(values)
    total    = sum(sorted_v)
    if total == 0.0:
        return 0.0   # all zeros → perfect equality
    cumulative = 0.0
    gini_sum   = 0.0
    for i, v in enumerate(sorted_v):
        cumulative += v
        gini_sum   += (2 * (i + 1) - n - 1) * v
    return gini_sum / (n * total)


def max_min_fairness_gap(values: List[float]) -> float:
    """
    Max-Min Fairness Gap: (max_shortage − min_shortage) / (max_shortage + ε).

    Returns 0 when all districts have equal shortage; approaches 1 when
    one district bears all the deprivation.

    Parameters
    ----------
    values : list of float
        Per-district shortage values (≥ 0).

    Returns
    -------
    float in [0, 1).
    """
    if not values:
        return 0.0
    hi  = max(values)
    lo  = min(values)
    return (hi - lo) / (hi + 1e-9)


def equity_penalty(
    shortages:      List[float],
    lambda_gini:    float = 0.3,
    lambda_maxmin:  float = 0.1,
) -> float:
    """
    Combined equity penalty added on top of the standard cost function.

    penalty = λ_gini × Gini(shortages) + λ_maxmin × MaxMinGap(shortages)

    Parameters
    ----------
    shortages     : per-district shortage (units).
    lambda_gini   : weight on the Gini term.
    lambda_maxmin : weight on the max-min gap term.

    Returns
    -------
    float  non-negative penalty scalar.
    """
    g = gini_coefficient(shortages)
    m = max_min_fairness_gap(shortages)
    return lambda_gini * g + lambda_maxmin * m


# ── Aggregate helpers ──────────────────────────────────────────────────────────

def district_shortages(state) -> List[float]:
    """Extract shortage list from an MDPState — convenience for agent code."""
    return [d.shortage for d in state.districts]
