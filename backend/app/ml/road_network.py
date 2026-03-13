"""
road_network.py
Stochastic Road Network with Flood-Driven Edge Failure Probabilities.

Research Basis
--------------
Improvement 3 from research_improvements.md:
    "Joint Inventory Allocation and Stochastic Routing
     with Dynamic Edge Failures predicted by LSTM sequences"

Model
-----
Each road edge (warehouse→district OR district→district) has a failure
probability derived from the DFSI (District Flood Severity Index) score:

    p_fail(n) = sigmoid(k × dfsi_n)

where k controls the steepness of the failure curve and dfsi_n ∈ [0, 1]
is the flood severity at the destination node.

A `sample_failure_mask()` draw returns a cost multiplier matrix:
  - Non-failed edges → original cost.
  - Failed edge      → infinity (impassable) OR large penalty cost.

Agents then use `effective_transport_cost()` to replace the direct
Haversine cost with the failure-adjusted cost.
"""

from __future__ import annotations

import math
import numpy as np
from typing import Dict, List, Optional, Tuple

from app.ml.mdp import DistrictState


# ── Math helpers ──────────────────────────────────────────────────────────────

def _sigmoid(x: float) -> float:
    """Numerically stable sigmoid."""
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres."""
    R    = 6_371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a    = (math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


# ── Road Network ──────────────────────────────────────────────────────────────

class RoadNetwork:
    """
    Stochastic road network where edge failure probability is determined by
    the DFSI flood severity score of the destination district.

    Parameters
    ----------
    districts  : list of DistrictState — nodes in the network.
    dfsi_scores: dict mapping district name → DFSI score ∈ [0, 1].
                 Higher DFSI = more severe flood = higher edge failure probability.
    failure_k  : float — steepness of the sigmoid failure curve (default 3.0).
    penalty_multiplier : float — cost multiplier when a road fails (must reroute).
                         Use float('inf') to model complete impassability.
    base_costs : dict mapping district name → baseline transport cost.
                 If None, uses district.truck_cost from DistrictState.
    """

    def __init__(
        self,
        districts:           List[DistrictState],
        dfsi_scores:         Optional[Dict[str, float]] = None,
        failure_k:           float = 3.0,
        penalty_multiplier:  float = 5.0,
        base_costs:          Optional[Dict[str, float]] = None,
    ):
        self.districts          = districts
        self.dfsi_scores        = dfsi_scores or {d.name: 0.0 for d in districts}
        self.failure_k          = failure_k
        self.penalty_multiplier = penalty_multiplier

        # Build baseline cost lookup
        if base_costs:
            self.base_costs = base_costs
        else:
            self.base_costs = {d.name: d.truck_cost for d in districts}

        # Pre-compute failure probabilities per district
        self.failure_probs: Dict[str, float] = {}
        for d in districts:
            dfsi = self.dfsi_scores.get(d.name, 0.0)
            self.failure_probs[d.name] = _sigmoid(self.failure_k * (dfsi - 0.5))

    # ── Core API ──────────────────────────────────────────────────────────────

    def sample_failure_mask(
        self, seed: Optional[int] = None
    ) -> Dict[str, bool]:
        """
        Sample a binary failure mask for all district edges.

        Returns
        -------
        dict: {district_name: True if road failed, False if passable}
        """
        if seed is not None:
            np.random.seed(seed)
        mask: Dict[str, bool] = {}
        for d in self.districts:
            p_fail = self.failure_probs[d.name]
            mask[d.name] = bool(np.random.random() < p_fail)
        return mask

    def effective_transport_cost(
        self,
        district_name:  str,
        failure_mask:   Dict[str, bool],
        vehicle:        str = "truck",
    ) -> float:
        """
        Return the effective transport cost for one vehicle trip to a district,
        accounting for road failure.

        Parameters
        ----------
        district_name : str
        failure_mask  : output of sample_failure_mask()
        vehicle       : "truck" or "uav" — UAVs ignore road failures.

        Returns
        -------
        float — effective cost per vehicle trip.
        """
        if vehicle == "uav":
            # UAVs are not affected by road failures
            ds = next((d for d in self.districts if d.name == district_name), None)
            return ds.uav_cost if ds else 0.0

        base = self.base_costs.get(district_name, 0.0)
        if failure_mask.get(district_name, False):
            return base * self.penalty_multiplier
        return base

    def compute_road_adjusted_cost(
        self,
        actions:      Dict[str, Dict[str, float]],
        failure_mask: Dict[str, bool],
        truck_cap:    float = 5_000.0,
        uav_cap:      float = 200.0,
    ) -> float:
        """
        Compute total transport cost for a set of allocation decisions,
        with road failure adjustments.

        Parameters
        ----------
        actions      : {district_name: {truck: units, uav: units}}
        failure_mask : from sample_failure_mask()

        Returns
        -------
        float — total transport cost adjusted for failed roads.
        """
        total = 0.0
        for d in self.districts:
            n = d.name
            truck_units = actions.get(n, {}).get("truck", 0.0)
            uav_units   = actions.get(n, {}).get("uav",   0.0)

            n_trucks = math.ceil(truck_units / truck_cap) if truck_units > 0 else 0
            n_uavs   = math.ceil(uav_units   / uav_cap)  if uav_units   > 0 else 0

            truck_cost_eff = self.effective_transport_cost(n, failure_mask, "truck")
            uav_cost_eff   = self.effective_transport_cost(n, failure_mask, "uav")
            total += n_trucks * truck_cost_eff + n_uavs * uav_cost_eff

        return total

    # ── Analytics ─────────────────────────────────────────────────────────────

    def network_risk_summary(self) -> Dict[str, float]:
        """
        Return a summary of the current network risk profile.

        Returns
        -------
        dict with keys:
            mean_failure_prob  : average edge failure probability
            max_failure_prob   : highest individual failure probability
            vulnerable_districts: list of district names with p_fail > 0.5
        """
        probs = list(self.failure_probs.values())
        return {
            "mean_failure_prob":     float(np.mean(probs)) if probs else 0.0,
            "max_failure_prob":      float(max(probs))     if probs else 0.0,
            "vulnerable_districts":  [
                name for name, p in self.failure_probs.items() if p > 0.5
            ],
        }
