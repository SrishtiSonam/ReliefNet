"""
mip_solver.py  (B.3)
Exact single-stage MIP allocation using PuLP + CBC solver.

Formulation (single commodity):
    min  Σ_n [ g(δ_tn) · h_tn  +  c^truck_n · y^truck_n  +  c^uav_n · y^uav_n ]

    s.t.
        Σ_n (y^truck_n · Q^T  +  y^uav_n · Q^U)  ≤  I^CW_t        [inventory]
        h_n  ≥  d̂_n  −  I_n  −  y^truck_n · Q^T  −  y^uav_n · Q^U  [shortage]
        h_n  ≥  0
        y^truck_n ∈  {0, 1, …, M^T}    (integer)
        y^uav_n   ∈  {0, 1, …, M^U}    (integer)

Where:
    g(δ)  = marginal deprivation cost at deprivation period δ
    Q^T   = truck capacity (units per trip)
    Q^U   = UAV   capacity (units per trip)
    M^T/U = max vehicle trips per district per period
    d̂_n   = demand estimate
    I_n   = current inventory at district n

Adapted from: van Steenbergen et al. (2023) — Section 4.2
"""

import math
import time
from typing import Dict, List, Optional, TYPE_CHECKING
from app.ml.base_agent import BaseAgent
from app.ml.config import SimulationConfig, DEFAULT_CONFIG
from app.ml.deprivation import marginal_deprivation_cost
from app.ml.mdp import MDPState, DistrictState, ScenarioGenerator
from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.ml.gnn_warm_start import GNNWarmStartPredictor

logger = get_logger(__name__)

try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    logger.warning("PuLP not installed — MIP solver will use greedy fallback. "
                   "Install with: pip install pulp")


class MIPSolver(BaseAgent):
    """Stateful MIP solver with optional GNN neural warm-starting."""

    def __init__(self,
                 truck_cap: float = 5_000.0,
                 uav_cap:   float = 200.0,
                 max_trucks_per_district: int = 10,
                 max_uavs_per_district:   int = 20,
                 time_limit_seconds: int = 30,
                 warm_start_predictor: "Optional[GNNWarmStartPredictor]" = None,
                 config: Optional[SimulationConfig] = None):
        cfg = config or DEFAULT_CONFIG
        self.truck_cap               = truck_cap
        self.uav_cap                 = uav_cap
        self.max_trucks              = max_trucks_per_district
        self.max_uavs                = max_uavs_per_district
        self.time_limit              = time_limit_seconds
        self.warm_start_predictor    = warm_start_predictor   # GNN neural warm-start (Improvement 5)
        self._last_solution: dict    = {}   # warm-start cache

    def get_action(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        """Alias so MIPSolver satisfies BaseAgent.get_action contract."""
        return self.solve(state)

    def evaluate(
        self,
        scenario_gen: ScenarioGenerator,
        initial_state: MDPState,
        n_eval: int = 30,
    ) -> Dict:
        """Run n_eval episodes and return cost statistics."""
        import numpy as np
        all_costs, all_dep = [], []
        max_dep = 0
        from app.ml.mdp import MDPTransition
        transition = MDPTransition(self.truck_cap, self.uav_cap)
        for _ in range(n_eval):
            path  = scenario_gen.generate_path()
            state = MDPState(epoch=0,
                              cw_inventory=initial_state.cw_inventory,
                              districts=[DistrictState(**d.__dict__)
                                         for d in initial_state.districts])
            ep_cost = ep_dep = 0.0
            for t in range(len(path["supply"])):
                actions = self.solve(state)
                cost    = transition.compute_cost(state, actions)
                for d in state.districts:
                    ep_dep += marginal_deprivation_cost(d.deprivation_time) * d.shortage
                    max_dep = max(max_dep, d.deprivation_time)
                ep_cost += cost
                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t] for d in path["demand_estimates"]}
                new_std = {d.name: d.demand_std for d in state.districts}
                state   = transition.transition(state, actions, real_d,
                                                 path["supply"][t], new_est, new_std)
            all_costs.append(ep_cost)
            all_dep.append(ep_dep)
        return {
            "method":               "mip",
            "total_cost":           float(np.mean(all_costs)),
            "total_cost_std":       float(np.std(all_costs)),
            "deprivation_cost":     float(np.mean(all_dep)),
            "transport_cost":       float(np.mean(all_costs) - np.mean(all_dep)),
            "max_deprivation_time": max_dep,
        }

    def solve(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        """
        Solve single-period relief allocation as a Mixed-Integer Program.
        Returns {district_name: {"truck": units, "uav": units}}
        """
        if not PULP_AVAILABLE:
            reason = "pulp_unavailable"
            logger.warning(f"MIP fallback reason: {reason} | "
                           f"districts={len(state.districts)} | inventory={state.cw_inventory:.1f}")
            return _greedy_fallback(state, self.truck_cap, self.uav_cap)

        if len(state.districts) == 0:
            reason = "zero_districts"
            logger.warning(f"MIP fallback reason: {reason} | "
                           f"districts=0 | inventory={state.cw_inventory:.1f}")
            return {}

        if state.cw_inventory <= 0:
            reason = "empty_inventory"
            logger.warning(f"MIP fallback reason: {reason} | "
                           f"districts={len(state.districts)} | inventory={state.cw_inventory:.1f}")
            return {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}

        districts = state.districts
        N = len(districts)

        # ── Build problem ─────────────────────────────────────────────────────────
        prob = pulp.LpProblem("flood_relief_allocation", pulp.LpMinimize)

        y_truck = [
            pulp.LpVariable(f"y_truck_{i}",
                             lowBound=0, upBound=self.max_trucks, cat="Integer")
            for i in range(N)
        ]
        y_uav = [
            pulp.LpVariable(f"y_uav_{i}",
                             lowBound=0, upBound=self.max_uavs, cat="Integer")
            for i in range(N)
        ]
        h = [pulp.LpVariable(f"h_{i}", lowBound=0) for i in range(N)]

        # ── Warm-start: GNN prediction (if available) else previous solution ──
        if self.warm_start_predictor is not None:
            try:
                gnn_hint = self.warm_start_predictor.generate_warm_start(state)
                self._last_solution = gnn_hint
                logger.debug(f"MIP warm-start: GNN prediction used for {N} districts")
            except Exception as exc:
                logger.warning(f"GNN warm-start failed ({exc}); falling back to previous solution")

        for i in range(N):
            tk_key  = f"y_truck_{i}"
            uav_key = f"y_uav_{i}"
            if tk_key in self._last_solution:
                y_truck[i].setInitialValue(self._last_solution[tk_key])
            if uav_key in self._last_solution:
                y_uav[i].setInitialValue(self._last_solution[uav_key])

        # ── Objective ─────────────────────────────────────────────────────────────
        deprivation_terms  = []
        transport_terms    = []
        for i, d in enumerate(districts):
            dep_weight = marginal_deprivation_cost(d.deprivation_time)
            deprivation_terms.append(dep_weight * h[i])
            transport_terms.append(d.truck_cost * y_truck[i] + d.uav_cost * y_uav[i])

        prob += pulp.lpSum(deprivation_terms) + pulp.lpSum(transport_terms), "TotalCost"

        # ── Constraints ───────────────────────────────────────────────────────────
        prob += (
            pulp.lpSum(
                y_truck[i] * self.truck_cap + y_uav[i] * self.uav_cap
                for i in range(N)
            ) <= state.cw_inventory,
            "CW_Inventory_Budget"
        )
        for i, d in enumerate(districts):
            alloc_i = y_truck[i] * self.truck_cap + y_uav[i] * self.uav_cap
            prob += (
                h[i] >= d.demand_estimate - d.inventory - alloc_i,
                f"Shortage_Link_{i}"
            )

        # ── Solve ─────────────────────────────────────────────────────────────────
        solver = pulp.PULP_CBC_CMD(
            msg=0,
            timeLimit=self.time_limit,
            gapRel=0.01,
            warmStart=bool(self._last_solution),
        )
        status_code = prob.solve(solver)
        status_str  = pulp.LpStatus[status_code]

        if status_str not in ("Optimal", "Feasible"):
            elapsed = time.perf_counter()  # approximate
            if status_str == "Infeasible":
                reason = "infeasible"
            elif elapsed >= self.time_limit * 0.95:
                reason = "timeout"
            else:
                reason = f"solver_status_{status_str}"
            logger.warning(f"MIP fallback reason: {reason} | "
                           f"districts={len(districts)} | inventory={state.cw_inventory:.1f}")
            return _greedy_fallback(state, self.truck_cap, self.uav_cap)

        # ── Extract solution and cache for warm-start ─────────────────────────
        actions: Dict[str, Dict[str, float]] = {}
        new_cache: dict = {}
        for i, d in enumerate(districts):
            n_trucks = int(round(pulp.value(y_truck[i]) or 0))
            n_uavs   = int(round(pulp.value(y_uav[i])   or 0))
            actions[d.name] = {
                "truck": float(n_trucks * self.truck_cap),
                "uav":   float(n_uavs   * self.uav_cap),
            }
            new_cache[f"y_truck_{i}"] = n_trucks
            new_cache[f"y_uav_{i}"]   = n_uavs

        self._last_solution = new_cache
        obj_val = pulp.value(prob.objective)
        logger.debug(f"MIP solved: status={status_str}, objective={obj_val:.2f}")
        return actions


# ─── Module-level singleton + convenience wrappers ────────────────────────────
_mip_singleton: MIPSolver = MIPSolver()


def solve_allocation_mip(
    state: MDPState,
    truck_cap: float = 5_000.0,
    uav_cap:   float = 200.0,
    max_trucks_per_district: int = 10,
    max_uavs_per_district:   int = 20,
    time_limit_seconds: int = 30,
) -> Dict[str, Dict[str, float]]:
    """Module-level convenience wrapper — uses the shared MIPSolver singleton."""
    global _mip_singleton
    # Reconfigure singleton if capacities differ
    if (truck_cap != _mip_singleton.truck_cap or uav_cap != _mip_singleton.uav_cap
            or max_trucks_per_district != _mip_singleton.max_trucks
            or max_uavs_per_district   != _mip_singleton.max_uavs):
        _mip_singleton = MIPSolver(truck_cap, uav_cap,
                                   max_trucks_per_district, max_uavs_per_district,
                                   time_limit_seconds)
    return _mip_singleton.solve(state)


def solve_allocation_mip_with_stats(
    state: MDPState,
    truck_cap: float = 5_000.0,
    uav_cap:   float = 200.0,
    **kwargs,
) -> Dict:
    """Same as solve_allocation_mip but also returns solver metadata."""
    import time
    t0 = time.perf_counter()
    actions = solve_allocation_mip(state, truck_cap, uav_cap, **kwargs)
    elapsed = time.perf_counter() - t0

    total_truck = sum(a["truck"] for a in actions.values())
    total_uav   = sum(a["uav"]   for a in actions.values())

    return {
        "actions":            actions,
        "solve_time_sec":     round(elapsed, 4),
        "total_truck_units":  total_truck,
        "total_uav_units":    total_uav,
        "inventory_used":     total_truck + total_uav,
        "inventory_remaining": max(0.0, state.cw_inventory - total_truck - total_uav),
    }


# ─── Greedy fallback (no PuLP dependency) ─────────────────────────────────────
def _greedy_fallback(state: MDPState,
                     truck_cap: float,
                     uav_cap: float) -> Dict[str, Dict[str, float]]:
    """
    Priority-based greedy heuristic used when PuLP is unavailable or
    the MIP times out.

    Priority rule:
        Score_n = g(δ_tn) × shortage_n + demand_estimate_n
    Allocate UAVs first to deprived districts, then trucks to highest-priority.
    """
    available = state.cw_inventory
    actions   = {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}

    # Sort by urgency score (descending)
    sorted_d = sorted(
        state.districts,
        key=lambda d: marginal_deprivation_cost(d.deprivation_time) * d.shortage
                      + d.demand_estimate,
        reverse=True,
    )

    # Phase 1: UAVs to actively deprived districts
    for d in sorted_d:
        if d.deprivation_time >= 1 and available >= uav_cap:
            n_uavs = min(
                math.ceil(d.demand_estimate / uav_cap),
                int(available // uav_cap),
                10,
            )
            uav_units = n_uavs * uav_cap
            actions[d.name]["uav"] = uav_units
            available -= uav_units

    # Phase 2: Trucks to highest-priority district(s)
    for d in sorted_d:
        if available < truck_cap:
            break
        n_trucks = min(int(available // truck_cap), 5)
        truck_units = n_trucks * truck_cap
        actions[d.name]["truck"] = truck_units
        available -= truck_units

    return actions