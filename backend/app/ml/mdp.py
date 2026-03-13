"""
MDP Formulation for Stochastic Dynamic Post-Flood Inventory Allocation
Adapted from: van Steenbergen et al. (2023) — SDPDIAP
Applied to: India Flood Relief using real district/flood datasets
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

# Re-export deprivation functions from deprivation.py for backward compatibility.
# Agents and routers that import from mdp will continue to work unchanged.
from app.ml.deprivation import (   # noqa: F401
    deprivation_cost,
    marginal_deprivation_cost,
    expected_deprivation_cost,
)


# ─── District State ───────────────────────────────────────────────────────────
@dataclass
class DistrictState:
    name:               str
    inventory:          float       # I_tn  — current inventory
    shortage:           float       # h_tn  — current shortage
    deprivation_time:   int         # δ_tn  — periods in deprivation
    demand_estimate:    float       # d_{t,t+1,n} — next period demand estimate
    demand_std:         float       # σ of demand
    uav_cost:           float       # c_nk for UAV
    truck_cost:         float       # c_nk for Truck


# ─── Global MDP State ─────────────────────────────────────────────────────────
@dataclass
class MDPState:
    epoch:          int
    cw_inventory:   float                       # I^CW_t
    districts:      List[DistrictState]         # One per district n ∈ N

    def to_feature_vector(self) -> np.ndarray:
        """Flat feature vector for NN-VFA input."""
        feats = [self.epoch, self.cw_inventory]
        for d in self.districts:
            feats += [d.inventory, d.deprivation_time,
                      d.demand_estimate, d.shortage]
        return np.array(feats, dtype=np.float32)


# ─── Post-Decision State ──────────────────────────────────────────────────────
@dataclass
class PostDecisionState:
    epoch:              int
    cw_inventory_x:     float
    districts_x:        List[Dict]   # {inv_x, deprivation_time, exp_deprivation_cost}


# ─── [Deprivation cost functions moved to deprivation.py] ────────────────────
# Kept here as thin wrappers via re-import above for backward compatibility.


# ─── Transition Function ──────────────────────────────────────────────────────
class MDPTransition:
    def __init__(self, truck_cap: float = 5000.0, uav_cap: float = 200.0):
        self.truck_cap = truck_cap
        self.uav_cap   = uav_cap

    def transition(self,
                   state: MDPState,
                   actions: Dict[str, Dict[str, float]],
                   realized_demands: Dict[str, float],
                   new_supply: float,
                   new_demand_estimates: Dict[str, float],
                   new_demand_stds: Dict[str, float]) -> MDPState:
        """
        St+1 = SM(St, xt, Wt+1)
        actions = {district_name: {truck: units, uav: units}}
        realized_demands = {district_name: actual demand realized}
        """
        new_districts = []
        for d in state.districts:
            n = d.name
            truck_alloc = actions.get(n, {}).get("truck", 0.0)
            uav_alloc   = actions.get(n, {}).get("uav",   0.0)
            total_alloc = truck_alloc + uav_alloc
            real_demand = realized_demands.get(n, d.demand_estimate)

            new_inv = max(0.0, d.inventory + total_alloc - real_demand)
            new_shortage = max(0.0, real_demand - (d.inventory + total_alloc))

            if d.inventory + total_alloc <= real_demand:
                new_dep_time = d.deprivation_time + 1
            else:
                new_dep_time = 0

            new_districts.append(DistrictState(
                name             = n,
                inventory        = new_inv,
                shortage         = new_shortage,
                deprivation_time = new_dep_time,
                demand_estimate  = new_demand_estimates.get(n, d.demand_estimate),
                demand_std       = new_demand_stds.get(n, d.demand_std),
                uav_cost         = d.uav_cost,
                truck_cost       = d.truck_cost,
            ))

        total_allocated = sum(
            actions.get(d.name, {}).get("truck", 0) +
            actions.get(d.name, {}).get("uav",   0)
            for d in state.districts
        )
        new_cw_inv = state.cw_inventory - total_allocated + new_supply

        return MDPState(
            epoch        = state.epoch + 1,
            cw_inventory = max(0.0, new_cw_inv),
            districts    = new_districts
        )

    def compute_cost(
        self,
        state:             MDPState,
        actions:           Dict[str, Dict[str, float]],
        road_failure_mask: Optional[Dict[str, bool]] = None,
    ) -> float:
        """
        C(St, xt) = deprivation costs + transportation costs.

        Parameters
        ----------
        state             : current MDPState
        actions           : {district: {truck: units, uav: units}}
        road_failure_mask : optional output of RoadNetwork.sample_failure_mask().
                            When provided, failed-road edges multiply the truck
                            cost by the network's penalty_multiplier (Improvement 3).
                            UAVs are NOT affected by road failures.
                            Default None → backward-compatible behaviour.
        """
        dep_cost   = 0.0
        trans_cost = 0.0
        for d in state.districts:
            n = d.name
            # Deprivation cost
            dep_cost += marginal_deprivation_cost(d.deprivation_time) * d.shortage
            # Transport cost
            truck_u  = actions.get(n, {}).get("truck", 0.0)
            uav_u    = actions.get(n, {}).get("uav",   0.0)
            n_trucks = np.ceil(truck_u / self.truck_cap) if truck_u > 0 else 0
            n_uavs   = np.ceil(uav_u   / self.uav_cap)   if uav_u   > 0 else 0

            truck_cost_n = d.truck_cost
            if road_failure_mask is not None and road_failure_mask.get(n, False):
                truck_cost_n *= 5.0   # default penalty multiplier for failed road
            trans_cost += n_trucks * truck_cost_n + n_uavs * d.uav_cost
        return dep_cost + trans_cost

    def compute_post_decision_state(self, state: MDPState,
                                    actions: Dict[str, Dict[str, float]]) -> PostDecisionState:
        """S^x_t = SM^x(St, xt)"""
        total_alloc = sum(
            actions.get(d.name, {}).get("truck", 0) +
            actions.get(d.name, {}).get("uav", 0)
            for d in state.districts
        )
        cw_x = state.cw_inventory - total_alloc

        districts_x = []
        for d in state.districts:
            alloc = (actions.get(d.name, {}).get("truck", 0) +
                     actions.get(d.name, {}).get("uav",   0))
            inv_x = d.inventory + alloc
            exp_dep = expected_deprivation_cost(
                inv_x, d.deprivation_time, d.demand_estimate, d.demand_std
            )
            districts_x.append({
                "name":                  d.name,
                "inv_x":                 inv_x,
                "deprivation_time":      d.deprivation_time,
                "exp_deprivation_cost":  exp_dep,
            })

        return PostDecisionState(
            epoch            = state.epoch,
            cw_inventory_x   = max(0.0, cw_x),
            districts_x      = districts_x
        )


# ─── Scenario Generator (Sample Paths) ───────────────────────────────────────
class ScenarioGenerator:
    """
    Generates stochastic sample paths using real INDOFLOODS
    precipitation data and District FloodImpact demand statistics.
    """
    def __init__(self, districts: List[DistrictState],
                 supply_mean: float, supply_std: float,
                 n_periods: int = 30):
        self.districts    = districts
        self.supply_mean  = supply_mean
        self.supply_std   = supply_std
        self.n_periods    = n_periods

    def generate_path(self) -> Dict:
        """Returns one sample path ω with supply and demand realizations."""
        # Vectorized draws — one call per distribution, then index per period
        supply_samples = np.maximum(
            0.0, np.random.normal(self.supply_mean, self.supply_std, self.n_periods)
        )

        demand_samples:   Dict[str, np.ndarray] = {}
        estimate_samples: Dict[str, np.ndarray] = {}
        for d in self.districts:
            demand_samples[d.name]   = np.maximum(
                0.0, np.random.normal(d.demand_estimate, d.demand_std, self.n_periods)
            )
            estimate_samples[d.name] = np.maximum(
                0.0, np.random.normal(d.demand_estimate, d.demand_std * 0.5, self.n_periods)
            )

        path = {
            "supply":           list(supply_samples),
            "demands":          {d.name: list(demand_samples[d.name])   for d in self.districts},
            "demand_estimates": {d.name: list(estimate_samples[d.name]) for d in self.districts},
        }
        return path