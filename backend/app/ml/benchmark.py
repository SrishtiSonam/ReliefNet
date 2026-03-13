"""
benchmark.py
BenchmarkRunner — standardised evaluation harness for all agents.

Instantiates, trains (where applicable), and evaluates all five allocation
agents side-by-side under the same random seeds for fair comparison.
Results are collected into a pandas DataFrame and optionally saved as CSV.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Optional

from app.ml.config import SimulationConfig, DEFAULT_CONFIG
from app.ml.mdp import MDPState, ScenarioGenerator, DistrictState
from app.ml.perfect_info import PerfectInfoSolver, gap_to_perfect
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class BenchmarkRunner:
    """
    Fair cross-agent evaluation harness.

    Usage
    -----
    runner = BenchmarkRunner(initial_state, scenario_gen, config)
    results_df = runner.to_dataframe()
    runner.save_report("benchmark_results.csv")
    """

    def __init__(
        self,
        initial_state: MDPState,
        scenario_gen:  ScenarioGenerator,
        config:        SimulationConfig = None,
        n_eval:        int = 30,
        seed:          int = 42,
    ):
        self.initial_state = initial_state
        self.scenario_gen  = scenario_gen
        self.config        = config or DEFAULT_CONFIG
        self.n_eval        = n_eval
        self.seed          = seed
        self._results: Optional[Dict] = None

    # ── Main runner ────────────────────────────────────────────────────────────

    def run_all(self) -> Dict:
        """
        Seed RNGs, instantiate all agents, evaluate, compute gaps.

        Returns
        -------
        dict keyed by agent method name, values are evaluate() result dicts
        augmented with 'gap_to_perfect_pct'.
        """
        # Lazy import agents to avoid circular imports at module load time
        from app.ml.rule_based import RuleBasedHeuristic
        from app.ml.dl_vfa import DLVFA
        from app.ml.nn_vfa import NNVFA
        from app.ml.ppo import PPOAgent
        from app.ml.mip_solver import MIPSolver
        from app.ml.constrained_ppo import ConstrainedPPOAgent
        from app.ml.mappo import MAPPOAgent
        from app.ml.attention_ppo import AttentionPPOAgent

        cfg     = self.config
        dists   = self.initial_state.districts
        results = {}

        # ── 1. Perfect-info lower bound ────────────────────────────────────────
        logger.info("Benchmarking: PerfectInfoSolver")
        self._seed()
        perfect = PerfectInfoSolver(
            districts=dists,
            n_periods=cfg.n_periods,
            truck_cap=cfg.truck_cap,
            uav_cap=cfg.uav_cap,
        )
        perfect_result = perfect.evaluate(self.scenario_gen, self.initial_state,
                                           n_eval=self.n_eval)
        results["perfect_info"] = perfect_result

        # ── 2. Rule-based heuristic ────────────────────────────────────────────
        logger.info("Benchmarking: RuleBasedHeuristic")
        self._seed()
        rb = RuleBasedHeuristic(
            districts=dists,
            n_periods=cfg.n_periods,
            truck_cap=cfg.truck_cap,
            uav_cap=cfg.uav_cap,
        )
        results["rule_based"] = rb.evaluate(self.scenario_gen, self.initial_state,
                                             n_eval=self.n_eval)

        # ── 3. DL-VFA ─────────────────────────────────────────────────────────
        logger.info("Benchmarking: DLVFA (training + evaluation)")
        self._seed()
        dl = DLVFA(
            districts=dists,
            n_periods=cfg.n_periods,
            truck_cap=cfg.truck_cap,
            uav_cap=cfg.uav_cap,
            alpha_init=cfg.dl_vfa_alpha_init,
            alpha_decay=cfg.dl_vfa_alpha_decay,
            eps_init=cfg.dl_vfa_eps_init,
            eps_decay=cfg.dl_vfa_eps_decay,
            discount=cfg.discount,
        )
        costs_dl = dl.train(self.scenario_gen, self.initial_state, n_episodes=2000)
        logger.info(
            f"DLVFA training complete | episodes=2000 | "
            f"mean_cost_last100={float(np.mean(costs_dl[-100:])):.2f}"
            if costs_dl else "DLVFA training complete | episodes=2000"
        )
        results["dl_vfa"] = dl.evaluate(self.scenario_gen, self.initial_state,
                                         n_eval=self.n_eval)

        # ── 4. NN-VFA ─────────────────────────────────────────────────────────
        logger.info("Benchmarking: NNVFA (training + evaluation)")
        self._seed()
        nn = NNVFA(
            districts=dists,
            n_periods=cfg.n_periods,
            truck_cap=cfg.truck_cap,
            uav_cap=cfg.uav_cap,
            lr=cfg.nn_vfa_lr,
            batch_size=cfg.nn_vfa_batch_size,
        )
        costs_nn = nn.train(self.scenario_gen, self.initial_state, n_episodes=3000)
        logger.info(
            f"NNVFA training complete | episodes=3000 | "
            f"mean_cost_last100={float(np.mean(costs_nn[-100:])):.2f}"
            if costs_nn else "NNVFA training complete | episodes=3000"
        )
        results["nn_vfa"] = nn.evaluate(self.scenario_gen, self.initial_state,
                                         n_eval=self.n_eval)

        # ── 5. PPO ────────────────────────────────────────────────────────────
        logger.info("Benchmarking: PPOAgent (training + evaluation)")
        self._seed()
        ppo = PPOAgent(
            districts=dists,
            n_periods=cfg.n_periods,
            truck_cap=cfg.truck_cap,
            uav_cap=cfg.uav_cap,
            lr=cfg.ppo_lr,
            clip_eps=cfg.ppo_clip_eps,
            gamma=cfg.ppo_gamma,
            gae_lambda=cfg.ppo_gae_lambda,
            n_epochs=cfg.ppo_n_epochs,
            batch_size=cfg.ppo_batch_size,
        )
        costs_ppo = ppo.train(self.scenario_gen, self.initial_state, n_episodes=10000)
        logger.info(
            f"PPOAgent training complete | episodes=10000 | "
            f"mean_cost_last100={float(np.mean(costs_ppo[-100:])):.2f}"
            if costs_ppo else "PPOAgent training complete | episodes=10000"
        )
        results["ppo"] = ppo.evaluate(self.scenario_gen, self.initial_state,
                                       n_eval=self.n_eval)

        # ── 6. MIP ────────────────────────────────────────────────────────────
        logger.info("Benchmarking: MIPSolver")
        self._seed()
        mip = MIPSolver(
            truck_cap=cfg.truck_cap,
            uav_cap=cfg.uav_cap,
            max_trucks_per_district=cfg.mip_max_trucks,
            max_uavs_per_district=cfg.mip_max_uavs,
            time_limit_seconds=cfg.mip_time_limit_sec,
        )
        results["mip"] = mip.evaluate(self.scenario_gen, self.initial_state,
                                       n_eval=self.n_eval)

        # ── Append gap_to_perfect for all non-perfect methods ─────────────────────
        for method, res in results.items():
            if method != "perfect_info":
                res["gap_to_perfect_pct"] = gap_to_perfect(res, perfect_result)
            else:
                res["gap_to_perfect_pct"] = 0.0

        # ── 7. Constrained PPO (Equity-Fair) ─────────────────────────────────
        logger.info("Benchmarking: ConstrainedPPOAgent (training + evaluation)")
        self._seed()
        cppo = ConstrainedPPOAgent(
            districts   = dists,
            n_periods   = cfg.n_periods,
            truck_cap   = cfg.truck_cap,
            uav_cap     = cfg.uav_cap,
            lr          = cfg.ppo_lr,
            clip_eps    = cfg.ppo_clip_eps,
            gamma       = cfg.ppo_gamma,
            gae_lambda  = cfg.ppo_gae_lambda,
            n_epochs    = cfg.ppo_n_epochs,
            batch_size  = cfg.ppo_batch_size,
        )
        cppo.train(self.scenario_gen, self.initial_state, n_episodes=5000)
        cppo_result = cppo.evaluate(self.scenario_gen, self.initial_state,
                                    n_eval=self.n_eval)
        cppo_result["gap_to_perfect_pct"] = gap_to_perfect(cppo_result, perfect_result)
        results["constrained_ppo"] = cppo_result

        # ── 8. MAPPO (Multi-Agent) ────────────────────────────────────────
        logger.info("Benchmarking: MAPPOAgent (training + evaluation)")
        self._seed()
        mappo = MAPPOAgent(
            districts       = dists,
            n_agents        = cfg.marl_n_agents,
            n_periods       = cfg.n_periods,
            truck_cap       = cfg.truck_cap,
            uav_cap         = cfg.uav_cap,
            comm_drop_prob  = cfg.marl_comm_drop_prob,
            lr              = cfg.ppo_lr,
        )
        mappo.train(self.scenario_gen, self.initial_state, n_episodes=3000)
        mappo_result = mappo.evaluate(self.scenario_gen, self.initial_state,
                                       n_eval=self.n_eval)
        mappo_result["gap_to_perfect_pct"] = gap_to_perfect(mappo_result, perfect_result)
        results["mappo"] = mappo_result

        # ── 9. AttentionPPO (Explainable) ──────────────────────────────────
        logger.info("Benchmarking: AttentionPPOAgent (training + evaluation)")
        self._seed()
        attn_ppo = AttentionPPOAgent(
            districts  = dists,
            n_periods  = cfg.n_periods,
            truck_cap  = cfg.truck_cap,
            uav_cap    = cfg.uav_cap,
            lr         = cfg.ppo_lr,
            d_model    = cfg.attn_d_model,
            n_heads    = cfg.attn_n_heads,
        )
        attn_ppo.train(self.scenario_gen, self.initial_state, n_episodes=5000)
        attn_result = attn_ppo.evaluate(self.scenario_gen, self.initial_state,
                                        n_eval=self.n_eval)
        attn_result["gap_to_perfect_pct"] = gap_to_perfect(attn_result, perfect_result)
        results["attention_ppo"] = attn_result

        self._results = results
        return results

    # ── Output helpers ─────────────────────────────────────────────────────────

    def to_dataframe(self) -> pd.DataFrame:
        """Return results as a flat comparison DataFrame."""
        results = self._results or self.run_all()
        rows = []
        for method, r in results.items():
            rows.append({
                "method":               method,
                "total_cost":           r.get("total_cost", float("nan")),
                "total_cost_std":       r.get("total_cost_std", float("nan")),
                "deprivation_cost":     r.get("deprivation_cost", float("nan")),
                "transport_cost":       r.get("transport_cost", float("nan")),
                "max_deprivation_time": r.get("max_deprivation_time", -1),
                "gap_to_perfect_pct":   r.get("gap_to_perfect_pct", float("nan")),
            })
        return pd.DataFrame(rows).sort_values("total_cost").reset_index(drop=True)

    def save_report(self, path: str) -> None:
        """Write the comparison DataFrame to CSV and log the path."""
        df = self.to_dataframe()
        df.to_csv(path, index=False)
        logger.info(f"Benchmark report saved to: {path}")

    # ── Internal ───────────────────────────────────────────────────────────────

    def _seed(self) -> None:
        np.random.seed(self.seed)
        if TORCH_AVAILABLE:
            import torch
            torch.manual_seed(self.seed)

    def _check_convergence(
        self,
        episode_costs: list,
        window: int = 100,
        threshold: float = 0.02,
    ) -> bool:
        """
        Returns True if training has converged.

        Convergence criterion: the relative change between the mean cost of
        the last `window` episodes and the mean cost of the `window` episodes
        immediately before that is below `threshold`.

        Parameters
        ----------
        episode_costs : list of per-episode costs returned by agent.train().
        window        : Number of episodes in each comparison window (default 100).
        threshold     : Maximum relative change to consider converged (default 0.02 = 2%).

        Returns
        -------
        bool
            True if converged, False if not enough data or still improving.
        """
        if len(episode_costs) < 2 * window:
            return False
        recent   = float(np.mean(episode_costs[-window:]))
        previous = float(np.mean(episode_costs[-2 * window:-window]))
        if previous == 0.0:
            return False
        return abs(recent - previous) / abs(previous) < threshold
