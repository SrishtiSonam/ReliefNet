"""
gymnasium_env.py
Standard Gymnasium Environment for Post-Flood Relief Allocation.

Research Basis
--------------
Improvement 6 from research_improvements.md:
    "ReliefEnv: A High-Fidelity Multi-Commodity Disaster Logistics
     Environment for Benchmarking RL Agents"

This module makes the flood-relief MDP publishable as a pip-installable
Gymnasium benchmark environment, enabling the wider RL research community
to run experiments on disaster logistics scenarios backed by real Indian
flood data.

Gym API
-------
  env = FloodReliefEnv(districts, scenario_gen, config)
  obs, info = env.reset(seed=42)
  obs, reward, terminated, truncated, info = env.step(action)

Action Space
------------
  Box(shape=(n_districts * 2,), low=0, high=1)
  Each pair (truck_ratio, uav_ratio) for district i defines the
  proportional share of CW inventory to send via each vehicle type.

Observation Space
-----------------
  Box(shape=(2 + n_districts * 4,),)   — output of MDPState.to_feature_vector()
  [epoch, cw_inventory, (inv, dep_time, demand, shortage) × n_districts]

Reward
------
  -C(s, x) — negative total cost (deprivation + transport) at each step.
"""

from __future__ import annotations

import copy
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.ml.mdp import MDPState, DistrictState, MDPTransition, ScenarioGenerator
from app.ml.config import SimulationConfig, DEFAULT_CONFIG

try:
    import gymnasium as gym
    from gymnasium import spaces
    GYM_AVAILABLE = True
except ImportError:
    GYM_AVAILABLE = False


# ── Environment Class ─────────────────────────────────────────────────────────

if GYM_AVAILABLE:
    class FloodReliefEnv(gym.Env):
        """
        Gymnasium-compatible environment wrapping the ReliefNet MDP.

        Parameters
        ----------
        initial_state : MDPState — starting inventory and district states.
        scenario_gen  : ScenarioGenerator — samples stochastic demand/supply paths.
        config        : SimulationConfig — hyper-parameters (periods, capacities, etc.)
        """

        metadata = {"render_modes": ["ansi"], "name": "FloodRelief-v1"}

        def __init__(
            self,
            initial_state: MDPState,
            scenario_gen:  ScenarioGenerator,
            config:        Optional[SimulationConfig] = None,
        ):
            super().__init__()
            self.initial_state = initial_state
            self.scenario_gen  = scenario_gen
            self.config        = config or DEFAULT_CONFIG
            self.n_districts   = len(initial_state.districts)
            self.n_periods     = self.config.n_periods
            self.truck_cap     = self.config.truck_cap
            self.uav_cap       = self.config.uav_cap
            self.transition    = MDPTransition(self.truck_cap, self.uav_cap)

            # ── Observation Space ──────────────────────────────────────────────
            obs_dim = 2 + self.n_districts * 4  # per MDPState.to_feature_vector()
            self.observation_space = spaces.Box(
                low   = np.full(obs_dim, -np.inf, dtype=np.float32),
                high  = np.full(obs_dim,  np.inf, dtype=np.float32),
                dtype = np.float32,
            )

            # ── Action Space ───────────────────────────────────────────────────
            # n_districts pairs of (truck_ratio, uav_ratio) ∈ [0, 1]
            self.action_space = spaces.Box(
                low   = np.zeros(self.n_districts * 2, dtype=np.float32),
                high  = np.ones(self.n_districts  * 2, dtype=np.float32),
                dtype = np.float32,
            )

            # Internal state variables
            self._state:  Optional[MDPState] = None
            self._path:   Optional[Dict]     = None
            self._step_t: int                = 0

        # ── Gymnasium API ──────────────────────────────────────────────────────

        def reset(
            self,
            seed: Optional[int] = None,
            options: Optional[dict] = None,
        ) -> Tuple[np.ndarray, Dict]:
            """Reset to a new episode. Returns (observation, info)."""
            super().reset(seed=seed)
            if seed is not None:
                np.random.seed(seed)

            self._state = MDPState(
                epoch        = 0,
                cw_inventory = self.initial_state.cw_inventory,
                districts    = [
                    DistrictState(**d.__dict__)
                    for d in self.initial_state.districts
                ],
            )
            self._path   = self.scenario_gen.generate_path()
            self._step_t = 0

            obs  = self._get_obs()
            info = {"epoch": 0, "cw_inventory": self._state.cw_inventory}
            return obs, info

        def step(
            self, action: np.ndarray,
        ) -> Tuple[np.ndarray, float, bool, bool, Dict]:
            """
            Apply action, transition state, return Gymnasium 5-tuple.

            Parameters
            ----------
            action : np.ndarray of shape (n_districts * 2,)
                     Values interpreted as proportional allocation ratios.

            Returns
            -------
            obs, reward, terminated, truncated, info
            """
            actions = self._action_to_dict(action)
            cost    = self.transition.compute_cost(self._state, actions)

            real_d  = {d: self._path["demands"][d][self._step_t]
                       for d in self._path["demands"]}
            new_est = {d: self._path["demand_estimates"][d][self._step_t]
                       for d in self._path["demand_estimates"]}
            new_std = {d.name: d.demand_std for d in self._state.districts}
            self._state = self.transition.transition(
                self._state, actions,
                real_d, self._path["supply"][self._step_t], new_est, new_std,
            )
            self._step_t += 1

            reward     = -float(cost)
            terminated = self._step_t >= self.n_periods
            truncated  = False
            obs        = self._get_obs()
            info = {
                "epoch":        self._step_t,
                "cost":         float(cost),
                "cw_inventory": float(self._state.cw_inventory),
                "shortages":    {d.name: d.shortage for d in self._state.districts},
            }
            return obs, reward, terminated, truncated, info

        def render(self, mode: str = "ansi") -> Optional[str]:
            """Print a simple text table of the current district states."""
            if self._state is None:
                return None
            lines = [
                f"=== FloodReliefEnv | Epoch {self._state.epoch} ===",
                f"CW Inventory: {self._state.cw_inventory:.0f} units",
                f"{'District':<15} {'Inv':>8} {'Shortage':>10} {'DepTime':>9} {'Demand':>10}",
                "-" * 55,
            ]
            for d in self._state.districts:
                lines.append(
                    f"{d.name:<15} {d.inventory:>8.0f} {d.shortage:>10.0f} "
                    f"{d.deprivation_time:>9} {d.demand_estimate:>10.0f}"
                )
            text = "\n".join(lines)
            if mode == "ansi":
                print(text)
            return text

        def close(self) -> None:
            pass

        # ── Internal helpers ───────────────────────────────────────────────────

        def _get_obs(self) -> np.ndarray:
            return self._state.to_feature_vector().astype(np.float32)

        def _action_to_dict(
            self, action: np.ndarray,
        ) -> Dict[str, Dict[str, float]]:
            """
            Map normalised action vector → concrete allocation dict.
            Clips total allocation to available inventory.
            """
            available = self._state.cw_inventory
            actions   = {d.name: {"truck": 0.0, "uav": 0.0}
                         for d in self._state.districts}

            # Clip action to [0, 1] and normalise per vehicle type
            action = np.clip(action, 0.0, 1.0)

            for i, d in enumerate(self._state.districts):
                t_ratio = float(action[i * 2])
                u_ratio = float(action[i * 2 + 1])
                truck_u = int((t_ratio * available) // self.truck_cap) * self.truck_cap
                uav_u   = int((u_ratio * available) // self.uav_cap)   * self.uav_cap
                actions[d.name]["truck"] = truck_u
                actions[d.name]["uav"]   = uav_u

            # Enforce budget
            total = sum(v["truck"] + v["uav"] for v in actions.values())
            if total > available + 1e-6:
                scale = available / (total + 1e-8)
                for k in actions:
                    actions[k]["truck"] *= scale
                    actions[k]["uav"]   *= scale

            return actions


def register_env() -> None:
    """
    Register FloodReliefEnv with Gymnasium's global registry.

    After calling this, you can create the env with:
        gym.make("FloodRelief-v1")
    """
    if not GYM_AVAILABLE:
        raise ImportError("gymnasium must be installed: pip install gymnasium>=0.29.0")
    # Import here to avoid errors when gymnasium is absent at module load
    import gymnasium as gym
    if "FloodRelief-v1" not in gym.envs.registry:
        gym.register(
            id           = "FloodRelief-v1",
            entry_point  = "app.ml.gymnasium_env:FloodReliefEnv",
            max_episode_steps = 30,
        )
