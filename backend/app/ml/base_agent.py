"""
base_agent.py
Abstract base class that every allocation agent must implement.

All agents (PPOAgent, DLVFA, NNVFA, RuleBasedHeuristic, MIPSolver,
PerfectInfoSolver) inherit from BaseAgent so routers and benchmark runners
can work with them polymorphically.
"""

from __future__ import annotations

import abc
from datetime import datetime, timezone
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.ml.mdp import MDPState, ScenarioGenerator


class BaseAgent(abc.ABC):
    """Abstract base class for all flood-relief allocation agents."""

    # ── Required: allocation decision ────────────────────────────────────────
    @abc.abstractmethod
    def get_action(self, state: "MDPState") -> Dict[str, Dict[str, float]]:
        """Return allocation dict {district_name: {\"truck\": units, \"uav\": units}}."""

    # ── Required: evaluation ─────────────────────────────────────────────────
    @abc.abstractmethod
    def evaluate(
        self,
        scenario_gen: "ScenarioGenerator",
        initial_state: "MDPState",
        n_eval: int = 30,
    ) -> Dict:
        """
        Run n_eval stochastic episodes and return a result dict.
        Every subclass MUST include at least the keys:
            method, total_cost, total_cost_std, deprivation_cost,
            transport_cost, max_deprivation_time
        """

    # ── Optional: training ───────────────────────────────────────────────────
    def train(
        self,
        scenario_gen: "ScenarioGenerator",
        initial_state: "MDPState",
        n_episodes: int = 1000,
    ) -> List[float]:
        """
        Train the agent.  Returns per-episode cost list.
        Agents without a training phase (e.g. RuleBasedHeuristic, MIPSolver)
        may leave this as a no-op.
        """
        return []

    # ── Concrete: evaluate with metadata ─────────────────────────────────────
    def evaluate_summary(
        self,
        scenario_gen: "ScenarioGenerator",
        initial_state: "MDPState",
        n_eval: int = 30,
    ) -> Dict:
        """
        Calls evaluate() and appends 'timestamp' and 'agent_class' fields
        for structured logging and result persistence.
        """
        result = self.evaluate(scenario_gen, initial_state, n_eval=n_eval)
        result["timestamp"]   = datetime.now(tz=timezone.utc).isoformat()
        result["agent_class"] = type(self).__name__
        return result
