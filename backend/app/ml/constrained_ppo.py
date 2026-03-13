"""
constrained_ppo.py
Equity-Constrained PPO for Fair Flood-Relief Allocation.

Research Basis
--------------
Improvement 1 from research_improvements.md:
    "Balancing Efficiency and Equity in Post-Flood Relief Allocation
     using Constrained Proximal Policy Optimization"

Method
------
Extends PPOAgent with a Lagrangian equity constraint.  At each training
step, the reward is augmented with an equity_penalty (Gini + Max-Min
gap) and a dual variable λ (the Lagrange multiplier) is updated via a
gradient ascent step on the constraint violation:

    Reward_aug = -cost - λ × equity_penalty(shortages)

The dual variable λ tracks how severely the equity constraint is
violated and auto-tightens/loosens the penalty automatically.

Both `gini` and `max_min_gap` statistics are appended to the evaluate()
result dict for fair comparison with vanilla PPOAgent.
"""

from __future__ import annotations

import numpy as np
import torch
from typing import Dict, List, Optional

from app.ml.ppo import PPOAgent
from app.ml.config import SimulationConfig, DEFAULT_CONFIG
from app.ml.mdp import MDPState, DistrictState, ScenarioGenerator
from app.ml.deprivation import marginal_deprivation_cost
from app.ml.equity import equity_penalty, gini_coefficient, max_min_fairness_gap


class ConstrainedPPOAgent(PPOAgent):
    """
    PPO with a Lagrangian equity constraint.

    The agent minimises total cost **and** guarantees that no single
    district bears a disproportionate share of the shortage burden.

    Extra Parameters
    ----------------
    lambda_gini     : float — Gini weight in equity penalty (default 0.3).
    lambda_maxmin   : float — Max-Min weight in equity penalty (default 0.1).
    dual_lr         : float — learning rate for the dual variable λ (default 0.01).
    equity_threshold: float — target max equity penalty; constraint is
                              satisfied when penalty ≤ threshold (default 0.05).
    """

    def __init__(
        self,
        districts:          List[DistrictState],
        n_periods:          int   = 30,
        truck_cap:          float = 5_000.0,
        uav_cap:            float = 200.0,
        lr:                 float = 0.0001,
        clip_eps:           float = 0.2,
        gamma:              float = 0.99,
        gae_lambda:         float = 0.95,
        n_epochs:           int   = 4,
        batch_size:         int   = 64,
        lambda_gini:        float = 0.3,
        lambda_maxmin:      float = 0.1,
        dual_lr:            float = 0.01,
        equity_threshold:   float = 0.05,
        config: Optional[SimulationConfig] = None,
    ):
        super().__init__(
            districts=districts, n_periods=n_periods,
            truck_cap=truck_cap, uav_cap=uav_cap,
            lr=lr, clip_eps=clip_eps, gamma=gamma,
            gae_lambda=gae_lambda, n_epochs=n_epochs,
            batch_size=batch_size, config=config,
        )
        cfg = config or DEFAULT_CONFIG
        self.lambda_gini       = getattr(cfg, "equity_lambda_gini",    lambda_gini)
        self.lambda_maxmin     = getattr(cfg, "equity_lambda_maxmin",  lambda_maxmin)
        self.dual_lr           = dual_lr
        self.equity_threshold  = equity_threshold
        self.dual_variable     = 1.0   # λ — starts at 1, adapts during training

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _augmented_reward(self, base_cost: float, state: MDPState) -> float:
        """
        Augmented reward = -base_cost  −  λ × equity_penalty(shortages).
        """
        shortages = [d.shortage for d in state.districts]
        pen = equity_penalty(shortages,
                             self.lambda_gini,
                             self.lambda_maxmin)
        return -base_cost - self.dual_variable * pen

    def _update_dual(self, equity_pen: float) -> None:
        """
        Dual gradient ascent: λ ← max(0, λ + dual_lr × (pen − threshold)).
        Increases λ when constraint violated, decreases when satisfied.
        """
        violation = equity_pen - self.equity_threshold
        self.dual_variable = max(0.0, self.dual_variable + self.dual_lr * violation)

    # ── Training (overrides PPOAgent.train) ───────────────────────────────────

    def train(
        self,
        scenario_gen:  ScenarioGenerator,
        initial_state: MDPState,
        n_episodes:    int = 60000,
    ) -> List[float]:
        """
        Same as PPOAgent.train() but with equity-augmented rewards and
        dual variable updates at the end of each episode.
        """
        episode_costs = []
        for ep in range(n_episodes):
            path  = scenario_gen.generate_path()
            state = MDPState(
                epoch=0, cw_inventory=initial_state.cw_inventory,
                districts=[DistrictState(**d.__dict__)
                           for d in initial_state.districts],
            )
            states_buf, lp_buf, reward_buf, val_buf = [], [], [], []
            ep_cost   = 0.0
            ep_eq_pen = 0.0

            for t in range(self.n_periods):
                s_feat = self._state_to_tensor(state).numpy().flatten()
                actions, log_prob, _ = self.get_action(state)
                cost   = self.transition.compute_cost(state, actions)
                ep_cost += cost

                shortages = [d.shortage for d in state.districts]
                pen = equity_penalty(shortages, self.lambda_gini, self.lambda_maxmin)
                ep_eq_pen += pen

                aug_reward = -cost - self.dual_variable * pen
                val        = self.critic(self._state_to_tensor(state)).item()

                states_buf.append(s_feat)
                lp_buf.append(log_prob.item())
                reward_buf.append(aug_reward)
                val_buf.append(val)

                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t]
                           for d in path["demand_estimates"]}
                new_std = {d.name: d.demand_std for d in state.districts}
                state   = self.transition.transition(
                    state, actions, real_d, path["supply"][t], new_est, new_std)

            dones = [False] * (self.n_periods - 1) + [True]
            advs  = self.compute_advantages(reward_buf, val_buf, dones)
            self.update(states_buf, lp_buf, reward_buf, advs)

            # Dual variable update using episode-average equity penalty
            avg_pen = ep_eq_pen / max(1, self.n_periods)
            self._update_dual(avg_pen)

            episode_costs.append(ep_cost)
        return episode_costs

    # ── Evaluation (overrides PPOAgent.evaluate) ──────────────────────────────

    def evaluate(
        self,
        scenario_gen:  ScenarioGenerator,
        initial_state: MDPState,
        n_eval:        int = 30,
    ) -> Dict:
        """
        Evaluate cost + equity metrics over n_eval episodes.
        Adds 'gini', 'max_min_gap', and 'dual_variable' to result dict.
        """
        all_costs, all_dep, all_gini, all_mm = [], [], [], []
        max_dep = 0

        for _ in range(n_eval):
            path  = scenario_gen.generate_path()
            state = MDPState(
                epoch=0, cw_inventory=initial_state.cw_inventory,
                districts=[DistrictState(**d.__dict__)
                           for d in initial_state.districts],
            )
            ep_cost = ep_dep = ep_gini = ep_mm = 0.0

            for t in range(self.n_periods):
                actions, _, _ = self.get_action(state)
                cost = self.transition.compute_cost(state, actions)
                shortages = [d.shortage for d in state.districts]
                ep_gini += gini_coefficient(shortages)
                ep_mm   += max_min_fairness_gap(shortages)
                for d in state.districts:
                    ep_dep += marginal_deprivation_cost(d.deprivation_time) * d.shortage
                    max_dep = max(max_dep, d.deprivation_time)
                ep_cost += cost
                real_d  = {d: path["demands"][d][t] for d in path["demands"]}
                new_est = {d: path["demand_estimates"][d][t]
                           for d in path["demand_estimates"]}
                new_std = {d.name: d.demand_std for d in state.districts}
                state   = self.transition.transition(
                    state, actions, real_d, path["supply"][t], new_est, new_std)

            all_costs.append(ep_cost)
            all_dep.append(ep_dep)
            all_gini.append(ep_gini / self.n_periods)
            all_mm.append(ep_mm / self.n_periods)

        return {
            "method":               "constrained_ppo",
            "total_cost":           float(np.mean(all_costs)),
            "total_cost_std":       float(np.std(all_costs)),
            "deprivation_cost":     float(np.mean(all_dep)),
            "transport_cost":       float(np.mean(all_costs) - np.mean(all_dep)),
            "max_deprivation_time": max_dep,
            "gini":                 float(np.mean(all_gini)),
            "max_min_gap":          float(np.mean(all_mm)),
            "dual_variable":        self.dual_variable,
        }
