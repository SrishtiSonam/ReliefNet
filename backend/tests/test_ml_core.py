"""
test_ml_core.py — unit tests for the ReliefNet ML core.

Run with: pytest backend/tests/test_ml_core.py -v
"""

import pytest
import numpy as np


# ─── Deprivation cost tests ────────────────────────────────────────────────────

def test_deprivation_cost_zero():
    from app.ml.deprivation import deprivation_cost
    assert deprivation_cost(0) == pytest.approx(0.0, abs=1e-9)


def test_deprivation_cost_increases():
    from app.ml.deprivation import deprivation_cost
    for n in range(10):
        assert deprivation_cost(n + 1) > deprivation_cost(n), (
            f"deprivation_cost({n+1}) not > deprivation_cost({n})"
        )


def test_marginal_deprivation_nonnegative():
    from app.ml.deprivation import marginal_deprivation_cost
    for n in range(15):
        assert marginal_deprivation_cost(n) >= 0.0, (
            f"marginal_deprivation_cost({n}) is negative"
        )


# ─── MDP transition tests ──────────────────────────────────────────────────────

def _make_simple_state(n_districts: int = 2, cw_inventory: float = 10_000.0):
    from app.ml.mdp import MDPState, DistrictState
    districts = [
        DistrictState(
            name=f"D{i}",
            inventory=500.0,
            shortage=0.0,
            deprivation_time=0,
            demand_estimate=300.0,
            demand_std=30.0,
            uav_cost=100.0,
            truck_cost=200.0,
        )
        for i in range(n_districts)
    ]
    return MDPState(epoch=0, cw_inventory=cw_inventory, districts=districts)


def test_mdp_transition_inventory_nonnegative():
    from app.ml.mdp import MDPState, DistrictState, MDPTransition
    state      = _make_simple_state()
    transition = MDPTransition()
    actions    = {d.name: {"truck": 1000.0, "uav": 200.0}
                  for d in state.districts}
    real_d     = {d.name: 400.0 for d in state.districts}
    new_est    = {d.name: 300.0 for d in state.districts}
    new_stds   = {d.name: 30.0  for d in state.districts}

    new_state  = transition.transition(state, actions, real_d, 5000.0,
                                        new_est, new_stds)

    assert new_state.cw_inventory >= 0, "CW inventory went negative"
    for d in new_state.districts:
        assert d.inventory >= 0.0, f"District {d.name} inventory is negative"


def test_mdp_transition_zero_allocation():
    from app.ml.mdp import MDPTransition
    state      = _make_simple_state(cw_inventory=10_000.0)
    transition = MDPTransition()
    actions    = {d.name: {"truck": 0.0, "uav": 0.0} for d in state.districts}
    real_d     = {d.name: 300.0 for d in state.districts}   # exact demand
    new_est    = {d.name: 300.0 for d in state.districts}
    new_stds   = {d.name: 30.0  for d in state.districts}

    new_state  = transition.transition(state, actions, real_d, 0.0,
                                        new_est, new_stds)

    for d in new_state.districts:
        # inventory should decrease by demand (floored at 0)
        assert d.inventory >= 0.0, f"District {d.name} inventory went negative"


# ─── MIP solver tests ──────────────────────────────────────────────────────────

def test_mip_solver_feasible_small():
    from app.ml.mip_solver import solve_allocation_mip
    state   = _make_simple_state(n_districts=2, cw_inventory=10_000.0)
    actions = solve_allocation_mip(state, truck_cap=5_000.0, uav_cap=200.0)

    total_allocated = sum(
        v["truck"] + v["uav"] for v in actions.values()
    )
    assert total_allocated <= state.cw_inventory + 1.0, (
        f"Allocated {total_allocated} exceeds inventory {state.cw_inventory}"
    )


def test_mip_solver_empty_inventory():
    from app.ml.mip_solver import solve_allocation_mip
    state   = _make_simple_state(cw_inventory=0.0)
    actions = solve_allocation_mip(state)

    for d_name, alloc in actions.items():
        assert alloc["truck"] == 0.0, f"Truck allocation for {d_name} should be 0"
        assert alloc["uav"]   == 0.0, f"UAV allocation for {d_name} should be 0"


# ─── Scenario generator tests ──────────────────────────────────────────────────

def test_scenario_generator_nonnegative():
    from app.ml.mdp import ScenarioGenerator
    state = _make_simple_state()
    gen   = ScenarioGenerator(
        districts=state.districts,
        supply_mean=5_000.0,
        supply_std=500.0,
        n_periods=30,
    )
    path = gen.generate_path()

    assert all(s >= 0 for s in path["supply"]), "Found negative supply in path"
    for d_name, demands in path["demands"].items():
        assert all(v >= 0 for v in demands), (
            f"Found negative demand for district {d_name}"
        )


# ─── BenchmarkRunner smoke test ────────────────────────────────────────────────

def test_benchmark_runner_runs():
    from app.ml.mdp import ScenarioGenerator
    from app.ml.config import SimulationConfig
    from app.ml.benchmark import BenchmarkRunner

    state = _make_simple_state(n_districts=1, cw_inventory=5_000.0)
    gen   = ScenarioGenerator(
        districts=state.districts,
        supply_mean=1_000.0,
        supply_std=100.0,
        n_periods=5,
    )
    cfg     = SimulationConfig(n_periods=5, mip_time_limit_sec=5)
    runner  = BenchmarkRunner(state, gen, config=cfg, n_eval=2, seed=0)
    results = runner.run_all()

    expected_keys = {"rule_based", "dl_vfa", "nn_vfa", "ppo", "mip", "perfect_info"}
    assert expected_keys.issubset(results.keys()), (
        f"Missing methods: {expected_keys - results.keys()}"
    )


# ─── Improvement 1: Equity metrics ────────────────────────────────────────────

def test_equity_gini_perfect_equality():
    """Gini of a uniform distribution must be 0."""
    from app.ml.equity import gini_coefficient
    assert gini_coefficient([0.0, 0.0, 0.0]) == pytest.approx(0.0, abs=1e-9)
    assert gini_coefficient([100.0, 100.0, 100.0]) == pytest.approx(0.0, abs=1e-6)


def test_equity_gini_worst_case():
    """All shortage in one district → Gini close to 1."""
    from app.ml.equity import gini_coefficient
    g = gini_coefficient([1000.0, 0.0, 0.0, 0.0])
    assert g > 0.6, f"Expected Gini > 0.6 for extreme inequality, got {g}"


def test_constrained_ppo_returns_equity_keys():
    """ConstrainedPPOAgent.evaluate() must include 'gini' and 'max_min_gap'."""
    from app.ml.mdp import ScenarioGenerator
    from app.ml.constrained_ppo import ConstrainedPPOAgent

    state = _make_simple_state(n_districts=2, cw_inventory=5_000.0)
    gen   = ScenarioGenerator(
        districts=state.districts,
        supply_mean=1_000.0,
        supply_std=100.0,
        n_periods=3,
    )
    agent = ConstrainedPPOAgent(
        districts=state.districts,
        n_periods=3,
        lambda_gini=0.3,
        lambda_maxmin=0.1,
    )
    result = agent.evaluate(gen, state, n_eval=2)
    assert "gini" in result, "'gini' key missing from ConstrainedPPOAgent.evaluate()"
    assert "max_min_gap" in result, "'max_min_gap' key missing"


# ─── Improvement 3: Road Network failure mask ──────────────────────────────────

def test_road_network_failure_mask_range():
    """Failure probability must lie in [0, 1] for any DFSI score."""
    from app.ml.road_network import RoadNetwork
    state = _make_simple_state(n_districts=3)
    dfsi  = {d.name: float(i) / 2 for i, d in enumerate(state.districts)}
    net   = RoadNetwork(state.districts, dfsi_scores=dfsi, failure_k=3.0)
    mask  = net.sample_failure_mask(seed=42)
    assert set(mask.keys()) == {d.name for d in state.districts}
    for name, failed in mask.items():
        assert isinstance(failed, bool), f"Expected bool for {name}, got {type(failed)}"


def test_road_network_uav_unaffected():
    """UAVs should NOT be penalised by road failures."""
    from app.ml.road_network import RoadNetwork
    state = _make_simple_state(n_districts=1)
    net   = RoadNetwork(state.districts, dfsi_scores={state.districts[0].name: 1.0})
    mask  = {state.districts[0].name: True}   # mark road as failed
    uav_cost = net.effective_transport_cost(state.districts[0].name, mask, vehicle="uav")
    assert uav_cost == pytest.approx(state.districts[0].uav_cost, rel=1e-6), (
        "UAV cost should be unchanged even when road fails"
    )


# ─── Improvement 4: AttentionPPOAgent explainability ──────────────────────────

def test_attention_ppo_explain_last_action():
    """explain_last_action() must return district names matching the state."""
    from app.ml.mdp import ScenarioGenerator
    from app.ml.attention_ppo import AttentionPPOAgent

    state = _make_simple_state(n_districts=2)
    agent = AttentionPPOAgent(districts=state.districts, n_periods=3)
    _     = agent.get_action(state)          # triggers attention computation
    expl  = agent.explain_last_action()

    assert set(expl.keys()) == {d.name for d in state.districts}, (
        f"explain_last_action() keys {set(expl.keys())} don't match districts"
    )
    total = sum(expl.values())
    assert abs(total - 1.0) < 1e-4, f"Attention weights should sum to ~1, got {total}"


# ─── Improvement 5: GNN warm-start output shape ────────────────────────────────

def test_gnn_warm_start_output_shape():
    """generate_warm_start() must return one y_truck_i and y_uav_i key per district."""
    from app.ml.gnn_warm_start import GNNWarmStartPredictor

    n = 3
    state = _make_simple_state(n_districts=n)
    pred  = GNNWarmStartPredictor(n_districts=n, hidden_dim=8)
    warm  = pred.generate_warm_start(state)

    expected_keys = {f"y_truck_{i}" for i in range(n)} | {f"y_uav_{i}" for i in range(n)}
    assert expected_keys == set(warm.keys()), (
        f"Warm-start keys {set(warm.keys())} don't match expected {expected_keys}"
    )
    for k, v in warm.items():
        assert isinstance(v, int) and v >= 0, f"Expected non-negative int for {k}, got {v}"


# ─── Improvement 6: Gymnasium environment ─────────────────────────────────────

def test_gymnasium_env_step_cycle():
    """FloodReliefEnv must run reset() + one step() without errors."""
    try:
        import gymnasium  # noqa: F401
    except ImportError:
        import pytest
        pytest.skip("gymnasium not installed")

    from app.ml.mdp import ScenarioGenerator
    from app.ml.gymnasium_env import FloodReliefEnv
    from app.ml.config import SimulationConfig

    state = _make_simple_state(n_districts=2, cw_inventory=5_000.0)
    gen   = ScenarioGenerator(
        districts=state.districts,
        supply_mean=1_000.0,
        supply_std=100.0,
        n_periods=5,
    )
    cfg = SimulationConfig(n_periods=5)
    env = FloodReliefEnv(state, gen, cfg)
    obs, info = env.reset(seed=0)

    assert obs.shape == env.observation_space.shape, (
        f"Observation shape mismatch: {obs.shape} vs {env.observation_space.shape}"
    )
    action = env.action_space.sample()
    obs2, reward, terminated, truncated, step_info = env.step(action)
    assert obs2.shape == env.observation_space.shape
    assert isinstance(reward, float)
    assert "cost" in step_info
    env.close()
