"""
perfect_info.py
PerfectInfoSolver — theoretical lower bound agent.

Receives the FULL future demand path at decision time and solves a
deterministic multi-period LP using PuLP to minimise total
deprivation + transport cost across all n_periods simultaneously.

Acts as the theoretical lower bound against which all stochastic agents
are benchmarked.
"""

from __future__ import annotations

import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.ml.base_agent import BaseAgent
from app.ml.deprivation import marginal_deprivation_cost
from app.ml.mdp import MDPState, MDPTransition, ScenarioGenerator, DistrictState
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import pulp
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False
    logger.warning("PuLP not installed — PerfectInfoSolver will use greedy fallback.")


class PerfectInfoSolver(BaseAgent):
    """
    Solves the deterministic multi-period LP with perfect future knowledge.
    This gives a lower bound on achievable cost for any stochastic agent.
    """

    def __init__(self,
                 districts: List[DistrictState],
                 n_periods: int = 30,
                 truck_cap: float = 5_000.0,
                 uav_cap:   float = 200.0,
                 time_limit_sec: int = 60):
        self.districts      = districts
        self.n_periods      = n_periods
        self.truck_cap      = truck_cap
        self.uav_cap        = uav_cap
        self.time_limit_sec = time_limit_sec
        self.transition     = MDPTransition(truck_cap, uav_cap)

    # ── BaseAgent contract ────────────────────────────────────────────────────

    def get_action(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        """Return an all-zero action dict (PerfectInfoSolver is not step-based)."""
        return {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}

    def evaluate(
        self,
        scenario_gen: ScenarioGenerator,
        initial_state: MDPState,
        n_eval: int = 30,
        path: Optional[Dict] = None,
    ) -> Dict:
        """
        Run n_eval episodes with perfect-information LP and return cost stats.

        Parameters
        ----------
        path : optional pre-generated scenario path.  If provided, n_eval is
               ignored and a single evaluation on that path is performed.
        """
        all_costs, all_dep = [], []
        max_dep = 0
        runs = 1 if path is not None else n_eval

        for _ in range(runs):
            p = path if path is not None else scenario_gen.generate_path()
            ep_cost, ep_dep, ep_max = self._solve_episode(initial_state, p)
            all_costs.append(ep_cost)
            all_dep.append(ep_dep)
            max_dep = max(max_dep, ep_max)

        return {
            "method":               "perfect_info",
            "total_cost":           float(np.mean(all_costs)),
            "total_cost_std":       float(np.std(all_costs)),
            "deprivation_cost":     float(np.mean(all_dep)),
            "transport_cost":       float(np.mean(all_costs) - np.mean(all_dep)),
            "max_deprivation_time": max_dep,
        }

    # ── Internal LP solve ─────────────────────────────────────────────────────

    def _solve_episode(
        self, initial_state: MDPState, path: Dict
    ):
        """Solve one deterministic multi-period LP given a realised path."""
        if not PULP_AVAILABLE:
            return self._greedy_episode(initial_state, path)

        N = len(self.districts)
        T = self.n_periods

        prob = pulp.LpProblem("perfect_info_allocation", pulp.LpMinimize)

        # Integer truck + UAV loads per (t, district)
        y_t = [[pulp.LpVariable(f"yt_{t}_{n}", lowBound=0, cat="Integer")
                for n in range(N)] for t in range(T)]
        y_u = [[pulp.LpVariable(f"yu_{t}_{n}", lowBound=0, cat="Integer")
                for n in range(N)] for t in range(T)]
        h   = [[pulp.LpVariable(f"h_{t}_{n}",  lowBound=0)
                for n in range(N)] for t in range(T)]

        # Objective: total deprivation + transport cost
        dep_terms   = []
        trans_terms = []
        for t in range(T):
            for n, d in enumerate(self.districts):
                # Use deprivation_time from initial state as starting point
                dep_weight = marginal_deprivation_cost(d.deprivation_time + t)
                dep_terms.append(dep_weight * h[t][n])
                trans_terms.append(d.truck_cost * y_t[t][n] + d.uav_cost * y_u[t][n])

        prob += pulp.lpSum(dep_terms) + pulp.lpSum(trans_terms)

        # ── C1: Shortage link with per-district inventory carry-forward ───────
        # running_inv is a Python float tracking district inventory across periods.
        # It starts at d.inventory and decreases by real_demand each period;
        # the LP variable alloc_t can top it up — the shortage var h absorbs deficits.
        for n, d in enumerate(self.districts):
            running_inv = d.inventory          # scalar starting balance
            for t in range(T):
                district_name = d.name
                real_demand = path["demands"].get(district_name,
                                                  [d.demand_estimate] * T)[t]
                alloc_t = y_t[t][n] * self.truck_cap + y_u[t][n] * self.uav_cap

                # h_{t,n} >= demand - (inventory_at_start_of_t + alloc_t)
                prob += (
                    h[t][n] >= real_demand - running_inv - alloc_t,
                    f"Shortage_{t}_{n}",
                )

                # Carry forward deterministic inventory component.
                # alloc_t is an LP variable so we only subtract real_demand here;
                # the LP freely chooses how much to allocate each period.
                running_inv = max(0.0, running_inv - real_demand)

        # ── C2: Single pooled CW budget constraint (flexible across all periods) ─
        # Total available = initial warehouse stock + all replenishments in horizon.
        # This is the correct lower bound: the LP may front-load or defer as needed.
        total_available = initial_state.cw_inventory + float(sum(path["supply"][:T]))
        prob += (
            pulp.lpSum(
                y_t[t][n] * self.truck_cap + y_u[t][n] * self.uav_cap
                for t in range(T) for n in range(N)
            ) <= total_available,
            "Pooled_CW_Budget",
        )

        prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=self.time_limit_sec))

        # Extract cost
        ep_cost = pulp.value(prob.objective) or 0.0
        ep_dep  = sum(
            pulp.value(h[t][n]) or 0.0
            for t in range(T) for n in range(N)
        )
        return ep_cost, ep_dep, T

    def _greedy_episode(self, initial_state: MDPState, path: Dict):
        """Fallback when PuLP is unavailable: simulate with uniform distribution."""
        state    = MDPState(
            epoch=0,
            cw_inventory=initial_state.cw_inventory,
            districts=[DistrictState(**d.__dict__) for d in initial_state.districts]
        )
        ep_cost = ep_dep = 0.0
        budget_per_step = state.cw_inventory / max(self.n_periods, 1)

        for t in range(self.n_periods):
            actions = {d.name: {"truck": budget_per_step / len(state.districts),
                                "uav": 0.0}
                       for d in state.districts}
            cost = self.transition.compute_cost(state, actions)
            ep_cost += cost
            for d in state.districts:
                ep_dep += marginal_deprivation_cost(d.deprivation_time) * d.shortage
            real_d   = {d: path["demands"][d][t] for d in path["demands"]}
            new_est  = {d: path["demand_estimates"][d][t] for d in path["demand_estimates"]}
            new_stds = {d.name: d.demand_std for d in state.districts}
            state = self.transition.transition(state, actions, real_d,
                                               path["supply"][t], new_est, new_stds)
        return ep_cost, ep_dep, self.n_periods


# ── Module-level utility ───────────────────────────────────────────────────────

def gap_to_perfect(agent_result: Dict, perfect_result: Dict) -> float:
    """
    Compute percentage optimality gap: (agent_cost - perfect_cost) / perfect_cost * 100.

    Parameters
    ----------
    agent_result   : evaluate() dict from any BaseAgent subclass.
    perfect_result : evaluate() dict from PerfectInfoSolver.

    Returns
    -------
    float
        Percentage gap ≥ 0.  Returns 0.0 if perfect_cost ≤ 0.
    """
    perfect_cost = perfect_result.get("total_cost", 0.0)
    agent_cost   = agent_result.get("total_cost", 0.0)
    if perfect_cost <= 0:
        return 0.0
    return round((agent_cost - perfect_cost) / perfect_cost * 100.0, 4)
