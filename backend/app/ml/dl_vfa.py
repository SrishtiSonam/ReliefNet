"""
Decomposed Linear Value Function Approximation (DL-VFA)
One linear VFA per district per decision epoch.
Adapted from: van Steenbergen et al. (2023)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy.optimize import linprog
from sklearn.linear_model import Ridge
from app.ml.base_agent import BaseAgent
from app.ml.config import SimulationConfig, DEFAULT_CONFIG
from app.ml.deprivation import marginal_deprivation_cost, expected_deprivation_cost
from app.ml.mdp import (MDPState, PostDecisionState, MDPTransition,
                         ScenarioGenerator, DistrictState)


class DLVFA(BaseAgent):
    def __init__(self,
                 districts: List[DistrictState],
                 n_periods: int = 30,
                 truck_cap: float = 5000.0,
                 uav_cap: float = 200.0,
                 buffer_size: int = 1000,
                 update_freq: int = 10,
                 alpha_init: float = 0.2,
                 alpha_decay: float = 0.99,
                 eps_init: float = 0.2,
                 eps_decay: float = 0.98,
                 discount: float = 0.9,
                 config: Optional[SimulationConfig] = None):
        cfg = config or DEFAULT_CONFIG

        self.districts   = districts
        self.n_periods   = n_periods
        self.truck_cap   = truck_cap
        self.uav_cap     = uav_cap
        self.buffer_size = buffer_size
        self.update_freq = update_freq
        self.alpha       = alpha_init
        self.alpha_decay = alpha_decay
        self.eps         = eps_init
        self.eps_decay   = eps_decay
        self.discount    = discount
        self.transition  = MDPTransition(truck_cap, uav_cap)
        self.n           = len(districts)

        # Weights: shape (n_periods, n_districts, 3)  — [inv_x, dep_time, exp_dep_cost]
        self.weights = np.zeros((n_periods, self.n, 3))

        # Experience buffer: list of (t, n_idx, features, future_cost)
        self.buffer: List[Tuple] = []

    # ── Feature vector per district ──────────────────────────────────────────
    def _features(self, inv_x: float, dep_time: int,
                  exp_dep_cost: float) -> np.ndarray:
        return np.array([inv_x, dep_time, exp_dep_cost], dtype=np.float32)

    # ── VFA value for one district ────────────────────────────────────────────
    def vfa_district(self, t: int, n_idx: int,
                     inv_x: float, dep_time: int, exp_dep_cost: float) -> float:
        phi = self._features(inv_x, dep_time, exp_dep_cost)
        return float(np.dot(self.weights[t, n_idx], phi))

    # ── Greedy action using MIP approximation (simplified LP) ────────────────
    def get_action(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        """
        Solve allocation using greedy minimization of:
        direct_cost + sum_n(VFA_n(post_decision_district_state))
        Simplified: allocate greedily by deprivation urgency + VFA weights.
        """
        available = state.cw_inventory
        actions = {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}

        # Score each district: direct deprivation + expected future cost
        scores = []
        for i, d in enumerate(state.districts):
            dep_c = marginal_deprivation_cost(d.deprivation_time) * d.shortage
            # Estimate VFA value if we send one truckload
            test_inv = d.inventory + self.truck_cap
            exp_dep  = expected_deprivation_cost(test_inv, d.deprivation_time,
                                                  d.demand_estimate, d.demand_std)
            future_c = self.vfa_district(state.epoch, i, test_inv,
                                         d.deprivation_time, exp_dep)
            scores.append((dep_c - future_c, i, d))  # higher = more urgent

        scores.sort(reverse=True)

        # First: UAVs to districts with active deprivation
        for _, i, d in scores:
            if d.deprivation_time >= 1 and available >= self.uav_cap:
                n_uavs = min(3, int(available // self.uav_cap))
                uav_units = n_uavs * self.uav_cap
                actions[d.name]["uav"] += uav_units
                available -= uav_units

        # Then: Trucks to highest-priority district
        if available >= self.truck_cap and scores:
            _, _, top_d = scores[0]
            n_trucks = int(available // self.truck_cap)
            truck_units = min(n_trucks * self.truck_cap, available)
            actions[top_d.name]["truck"] += truck_units
            available -= truck_units

        return actions

    # ── Warm-up heuristic ─────────────────────────────────────────────────────
    def warmup_action(self, state: MDPState) -> Dict[str, Dict[str, float]]:
        available = state.cw_inventory
        actions = {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}
        thresh = np.random.randint(1, 4)
        for d in state.districts:
            if d.deprivation_time >= thresh and available >= self.uav_cap:
                n_uavs = np.random.randint(1, 4)
                uav_u = min(n_uavs * self.uav_cap, available)
                actions[d.name]["uav"] = uav_u
                available -= uav_u
        if available >= self.truck_cap and state.districts:
            chosen = np.random.choice(state.districts)
            actions[chosen.name]["truck"] = min(self.truck_cap, available)
        return actions

    # ── Update weights via Ridge regression ──────────────────────────────────
    def update_weights(self, episode: int):
        if len(self.buffer) < 50:
            return
        # Remove outliers (Q3 + 1.5*IQR)
        costs = np.array([b[3] for b in self.buffer])
        q3, q1 = np.percentile(costs, [75, 25])
        iqr = q3 - q1
        clean = [b for b in self.buffer if b[3] <= q3 + 1.5 * iqr]

        for n_idx in range(self.n):
            for t in range(self.n_periods):
                subset = [(b[2], b[3]) for b in clean if b[0] == t and b[1] == n_idx]
                if len(subset) < 5:
                    continue
                X = np.array([s[0] for s in subset])
                y = np.array([s[1] for s in subset])
                model = Ridge(alpha=1.0)
                model.fit(X, y)
                new_w = model.coef_
                # Smoothed update
                self.weights[t, n_idx] = (
                    (1 - self.alpha) * self.weights[t, n_idx] + self.alpha * new_w
                )

        self.alpha *= self.alpha_decay
        self.eps   *= self.eps_decay

    # ── Training loop ─────────────────────────────────────────────────────────
    def train(self, scenario_gen: ScenarioGenerator,
              initial_state: MDPState, n_episodes: int = 1000) -> List[float]:
        episode_costs = []

        for ep in range(n_episodes):
            path   = scenario_gen.generate_path()
            state  = MDPState(epoch=0,
                               cw_inventory=initial_state.cw_inventory,
                               districts=[DistrictState(**d.__dict__)
                                          for d in initial_state.districts])
            ep_cost = 0.0
            ep_buffer = []
            step_costs = []

            for t in range(self.n_periods):
                # ε-greedy
                if np.random.rand() < self.eps:
                    actions = self.warmup_action(state)
                else:
                    actions = self.get_action(state)

                cost = self.transition.compute_cost(state, actions)
                pds  = self.transition.compute_post_decision_state(state, actions)
                ep_cost += cost
                step_costs.append(cost)

                # Store in buffer
                for i, dx in enumerate(pds.districts_x):
                    phi = self._features(dx["inv_x"], dx["deprivation_time"],
                                         dx["exp_deprivation_cost"])
                    ep_buffer.append((t, i, phi, 0.0))  # future cost filled recursively

                # Transition
                real_d   = {d: path["demands"][d][t] for d in path["demands"]}
                new_est  = {d: path["demand_estimates"][d][t] for d in path["demand_estimates"]}
                new_stds = {d.name: d.demand_std for d in state.districts}
                new_sup  = path["supply"][t]

                state = self.transition.transition(
                    state, actions, real_d, new_sup, new_est, new_stds
                )

            # Reverse-pass: compute full discounted return G_t = cost_t + γ·G_{t+1}
            # Iterate by time-step (not by flat buffer index) to avoid off-by-one
            # modular arithmetic that fires G accumulation at wrong boundaries.
            G = 0.0
            n_districts = self.n
            for t_step in range(self.n_periods - 1, -1, -1):
                G = step_costs[t_step] + self.discount * G
                for n_idx in range(n_districts):
                    idx = t_step * n_districts + n_idx
                    t_, n_i, phi, _ = ep_buffer[idx]
                    ep_buffer[idx] = (t_, n_i, phi, G)


            # Add to rolling buffer (FIFO)
            self.buffer.extend(ep_buffer)
            if len(self.buffer) > self.buffer_size:
                self.buffer = self.buffer[-self.buffer_size:]

            if (ep + 1) % self.update_freq == 0:
                self.update_weights(ep)

            episode_costs.append(ep_cost)

        return episode_costs

    # ── Run one evaluation episode ────────────────────────────────────────────
    def evaluate(self, scenario_gen: ScenarioGenerator,
                 initial_state: MDPState, n_eval: int = 30) -> Dict:
        all_costs, all_dep, all_trans = [], [], []
        all_decisions = []
        max_dep_time = 0

        for _ in range(n_eval):
            path  = scenario_gen.generate_path()
            state = MDPState(epoch=0,
                              cw_inventory=initial_state.cw_inventory,
                              districts=[DistrictState(**d.__dict__)
                                         for d in initial_state.districts])
            ep_cost = ep_dep = ep_trans = 0.0

            for t in range(self.n_periods):
                actions = self.get_action(state)
                cost    = self.transition.compute_cost(state, actions)

                for d in state.districts:
                    ep_dep   += marginal_deprivation_cost(d.deprivation_time) * d.shortage
                    max_dep_time = max(max_dep_time, d.deprivation_time)

                ep_cost  += cost
                all_decisions.append({"epoch": t, "actions": actions})

                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t] for d in path["demand_estimates"]}
                new_stds= {d.name: d.demand_std for d in state.districts}
                state   = self.transition.transition(
                    state, actions, real_d, path["supply"][t], new_est, new_stds
                )

            all_costs.append(ep_cost)
            all_dep.append(ep_dep)
            all_trans.append(ep_cost - ep_dep)

        return {
            "method": "dl_vfa",
            "total_cost":       float(np.mean(all_costs)),
            "total_cost_std":   float(np.std(all_costs)),
            "deprivation_cost": float(np.mean(all_dep)),
            "transport_cost":   float(np.mean(all_trans)),
            "max_deprivation_time": max_dep_time,
            "decisions":        all_decisions,
        }