"""
multi_commodity.py  (B.5)
Multi-Commodity Relief Allocation

Commodities: food, water, medicine, shelter_materials
Each commodity has its own:
    - urgency_weight   : multiplier on the deprivation cost function
    - demand_fraction  : fraction of total district demand attributed to it
    - unit_weight_kg   : kg per relief-unit (used for vehicle load planning)
    - shelf_life_days  : days before commodity expires (inf = non-perishable)

The MDP state is extended to track per-commodity inventories, shortages,
and deprivation times. The MIP is solved separately per commodity
(decomposed by commodity for tractability), with a shared vehicle fleet
budget across commodities.

Adapted from: multi-item stochastic inventory literature.
"""

import math
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False


# ─── Commodity specification ──────────────────────────────────────────────────
class CommodityType(str, Enum):
    FOOD     = "food"
    WATER    = "water"
    MEDICINE = "medicine"
    SHELTER  = "shelter"


@dataclass(frozen=True)
class CommoditySpec:
    urgency_weight:   float   # g(δ) multiplier
    demand_fraction:  float   # fraction of total demand
    unit_weight_kg:   float   # kg per unit
    shelf_life_days:  float   # math.inf = no expiry


COMMODITY_SPECS: Dict[CommodityType, CommoditySpec] = {
    CommodityType.FOOD:     CommoditySpec(urgency_weight=1.5,  demand_fraction=0.35, unit_weight_kg=1.0, shelf_life_days=3.0),
    CommodityType.WATER:    CommoditySpec(urgency_weight=2.0,  demand_fraction=0.40, unit_weight_kg=1.0, shelf_life_days=30.0),
    CommodityType.MEDICINE: CommoditySpec(urgency_weight=3.0,  demand_fraction=0.10, unit_weight_kg=0.1, shelf_life_days=365.0),
    CommodityType.SHELTER:  CommoditySpec(urgency_weight=0.8,  demand_fraction=0.15, unit_weight_kg=5.0, shelf_life_days=math.inf),
}

ALL_COMMODITIES = list(CommodityType)
COMMODITY_KEYS  = [c.value for c in ALL_COMMODITIES]


# ─── Multi-commodity district state ──────────────────────────────────────────
@dataclass
class MCDistrictState:
    """Extended district state with per-commodity tracking."""
    name:             str
    inventories:      Dict[str, float]  # commodity → units
    shortages:        Dict[str, float]  # commodity → shortage units
    dep_times:        Dict[str, int]    # commodity → deprivation periods
    demand_estimates: Dict[str, float]  # commodity → expected demand (units/period)
    demand_stds:      Dict[str, float]  # commodity → std dev
    uav_cost:         float
    truck_cost:       float

    @classmethod
    def from_single_commodity(cls,
                               name: str,
                               total_inventory: float,
                               total_shortage: float,
                               dep_time: int,
                               total_demand: float,
                               demand_std: float,
                               uav_cost: float,
                               truck_cost: float) -> "MCDistrictState":
        """Split single-commodity state across commodities by demand_fraction."""
        return cls(
            name   = name,
            inventories      = {c: total_inventory * COMMODITY_SPECS[CommodityType(c)].demand_fraction
                                 for c in COMMODITY_KEYS},
            shortages        = {c: total_shortage  * COMMODITY_SPECS[CommodityType(c)].demand_fraction
                                 for c in COMMODITY_KEYS},
            dep_times        = {c: dep_time for c in COMMODITY_KEYS},
            demand_estimates = {c: total_demand * COMMODITY_SPECS[CommodityType(c)].demand_fraction
                                 for c in COMMODITY_KEYS},
            demand_stds      = {c: demand_std  * COMMODITY_SPECS[CommodityType(c)].demand_fraction
                                 for c in COMMODITY_KEYS},
            uav_cost   = uav_cost,
            truck_cost = truck_cost,
        )

    def total_deprivation_cost(self) -> float:
        from app.ml.deprivation import marginal_deprivation_cost
        total = 0.0
        for c in COMMODITY_KEYS:
            spec = COMMODITY_SPECS[CommodityType(c)]
            g    = marginal_deprivation_cost(self.dep_times[c])
            total += spec.urgency_weight * g * self.shortages[c]
        return total


# ─── Multi-commodity MDP transition ──────────────────────────────────────────
def mc_transition(
    district: MCDistrictState,
    actions:  Dict[str, Dict[str, float]],   # commodity → {truck, uav}
    realized: Dict[str, float],              # commodity → actual demand
    n_periods: int = 1,
) -> MCDistrictState:
    """
    Update one district state for one period.
    Handles perishability: inventory reduced by expired fraction.
    """
    new_inv    = {}
    new_short  = {}
    new_dep    = {}

    for c in COMMODITY_KEYS:
        spec         = COMMODITY_SPECS[CommodityType(c)]
        alloc        = actions.get(c, {}).get("truck", 0.0) + actions.get(c, {}).get("uav", 0.0)
        real_demand  = realized.get(c, district.demand_estimates[c])
        inv_before   = district.inventories[c] + alloc

        # Perishability: fraction lost per period
        if spec.shelf_life_days < math.inf:
            survival_rate = max(0.0, 1.0 - (n_periods / spec.shelf_life_days))
            inv_before   *= survival_rate

        new_i = max(0.0, inv_before - real_demand)
        new_s = max(0.0, real_demand - inv_before)

        new_inv[c]   = new_i
        new_short[c] = new_s
        new_dep[c]   = district.dep_times[c] + 1 if inv_before <= real_demand else 0

    return MCDistrictState(
        name             = district.name,
        inventories      = new_inv,
        shortages        = new_short,
        dep_times        = new_dep,
        demand_estimates = district.demand_estimates,
        demand_stds      = district.demand_stds,
        uav_cost         = district.uav_cost,
        truck_cost       = district.truck_cost,
    )


# ─── Multi-commodity MIP allocation ──────────────────────────────────────────
def solve_multi_commodity_mip(
    districts:       List[MCDistrictState],
    cw_inventories:  Dict[str, float],    # commodity → available units at CW
    truck_cap_kg:    float = 5_000.0,
    uav_cap_kg:      float = 200.0,
    max_trucks:      int   = 10,
    max_uavs:        int   = 20,
    time_limit_sec:  int   = 60,
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Solve multi-commodity allocation.

    Decision variables per (commodity, district):
        y^truck_{c,n} ∈ Z+  (integer truck loads)
        y^uav_{c,n}   ∈ Z+  (integer UAV loads)

    Returns:
        {district_name: {commodity: {"truck": units, "uav": units}}}
    """
    if not PULP_AVAILABLE:
        logger.warning("PuLP unavailable — using greedy multi-commodity allocation.")
        return _greedy_mc(districts, cw_inventories, truck_cap_kg, uav_cap_kg)

    from app.ml.deprivation import marginal_deprivation_cost

    # Initialise blank action dict
    actions: Dict[str, Dict[str, Dict[str, float]]] = {
        d.name: {c: {"truck": 0.0, "uav": 0.0} for c in COMMODITY_KEYS}
        for d in districts
    }

    N = len(districts)
    if N == 0:
        return actions

    # Solve commodity-by-commodity (decomposed for tractability)
    for comm in COMMODITY_KEYS:
        spec  = COMMODITY_SPECS[CommodityType(comm)]
        avail = cw_inventories.get(comm, 0.0)
        if avail <= 0.0:
            continue

        # Units per vehicle load
        truck_units = truck_cap_kg / spec.unit_weight_kg
        uav_units   = uav_cap_kg   / spec.unit_weight_kg

        prob = pulp.LpProblem(f"mc_alloc_{comm}", pulp.LpMinimize)

        y_tr  = [pulp.LpVariable(f"yt_{comm}_{i}", lowBound=0, upBound=max_trucks, cat="Integer") for i in range(N)]
        y_uav = [pulp.LpVariable(f"yu_{comm}_{i}", lowBound=0, upBound=max_uavs,   cat="Integer") for i in range(N)]
        h     = [pulp.LpVariable(f"h_{comm}_{i}",  lowBound=0) for i in range(N)]

        # Objective: urgency-weighted deprivation + transport
        dep_terms   = []
        trans_terms = []
        for i, d in enumerate(districts):
            g = marginal_deprivation_cost(d.dep_times.get(comm, 0))
            dep_terms.append(spec.urgency_weight * g * h[i])
            trans_terms.append(d.truck_cost * y_tr[i] + d.uav_cost * y_uav[i])

        prob += pulp.lpSum(dep_terms) + pulp.lpSum(trans_terms)

        # C1: CW inventory budget (in units)
        prob += pulp.lpSum(
            y_tr[i] * truck_units + y_uav[i] * uav_units for i in range(N)
        ) <= avail

        # C2: Shortage linkage
        for i, d in enumerate(districts):
            alloc_i = y_tr[i] * truck_units + y_uav[i] * uav_units
            prob += h[i] >= d.demand_estimates.get(comm, 0.0) - d.inventories.get(comm, 0.0) - alloc_i

        prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit_sec))

        for i, d in enumerate(districts):
            nt = int(round(pulp.value(y_tr[i])  or 0))
            nu = int(round(pulp.value(y_uav[i]) or 0))
            actions[d.name][comm]["truck"] = float(nt * truck_units)
            actions[d.name][comm]["uav"]   = float(nu * uav_units)

    return actions


def compute_mc_cost(
    districts: List[MCDistrictState],
    actions:   Dict[str, Dict[str, Dict[str, float]]],
    truck_cap_kg: float = 5_000.0,
    uav_cap_kg:   float = 200.0,
) -> float:
    """Total cost = Σ commodity deprivation costs + Σ transport costs."""
    from app.ml.deprivation import marginal_deprivation_cost
    total = 0.0
    for d in districts:
        for comm in COMMODITY_KEYS:
            spec = COMMODITY_SPECS[CommodityType(comm)]
            g    = marginal_deprivation_cost(d.dep_times.get(comm, 0))
            total += spec.urgency_weight * g * d.shortages.get(comm, 0.0)

            a  = actions.get(d.name, {}).get(comm, {})
            tu = a.get("truck", 0.0)
            uu = a.get("uav",   0.0)
            unit_w = spec.unit_weight_kg
            n_trucks = math.ceil(tu / (truck_cap_kg / unit_w)) if tu > 0 else 0
            n_uavs   = math.ceil(uu / (uav_cap_kg   / unit_w)) if uu > 0 else 0
            total += n_trucks * d.truck_cost + n_uavs * d.uav_cost

    return total


# ─── Greedy fallback ──────────────────────────────────────────────────────────
def _greedy_mc(
    districts:      List[MCDistrictState],
    cw_inventories: Dict[str, float],
    truck_cap_kg:   float,
    uav_cap_kg:     float,
) -> Dict[str, Dict[str, Dict[str, float]]]:
    from app.ml.deprivation import marginal_deprivation_cost

    actions: Dict[str, Dict[str, Dict[str, float]]] = {
        d.name: {c: {"truck": 0.0, "uav": 0.0} for c in COMMODITY_KEYS}
        for d in districts
    }
    avail = {c: cw_inventories.get(c, 0.0) for c in COMMODITY_KEYS}

    for comm in COMMODITY_KEYS:
        spec       = COMMODITY_SPECS[CommodityType(comm)]
        truck_u    = truck_cap_kg / spec.unit_weight_kg
        uav_u      = uav_cap_kg   / spec.unit_weight_kg
        sorted_d   = sorted(districts,
                             key=lambda d: (marginal_deprivation_cost(d.dep_times.get(comm, 0))
                                            * d.shortages.get(comm, 0.0)), reverse=True)

        # UAVs first
        for d in sorted_d:
            if d.dep_times.get(comm, 0) >= 1 and avail[comm] >= uav_u:
                n_uavs = min(3, int(avail[comm] // uav_u))
                send   = n_uavs * uav_u
                actions[d.name][comm]["uav"] = send
                avail[comm] -= send

        # Trucks to all districts in descending demand order
        for d in sorted_d:
            if avail[comm] < truck_u:
                break
            n_trucks = min(int(avail[comm] // truck_u), 5)
            send = n_trucks * truck_u
            actions[d.name][comm]["truck"] = send
            avail[comm] -= send

    return actions