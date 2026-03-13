"""
explainability.py
Stateless explanation helpers for the ReliefNet RL agents.

Research Basis
--------------
Improvement 4 from research_improvements.md:
    "Trusting the Machine: Explainable Deep Reinforcement Learning
     Interfaces for Disaster Operations Management"

These helpers convert attention weights and allocation decisions into
human-readable JSON suitable for display on the React GIS map and for
reporting to disaster management officers.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


# ── District Ranking ──────────────────────────────────────────────────────────

def top_k_districts(
    attention_weights: Dict[str, float],
    k: int = 3,
) -> List[Tuple[str, float]]:
    """
    Return the top-k districts ranked by attention weight.

    Parameters
    ----------
    attention_weights : {district_name: weight}  — from AttentionPPOAgent.explain_last_action()
    k                 : int — number of districts to return.

    Returns
    -------
    List of (district_name, weight) tuples sorted descending by weight.
    """
    ranked = sorted(attention_weights.items(), key=lambda x: x[1], reverse=True)
    return ranked[:k]


# ── Decision Explanation ──────────────────────────────────────────────────────

def build_decision_explanation(
    state,
    actions:            Dict[str, Dict[str, float]],
    attention_weights:  Dict[str, float],
    top_k:              int = 3,
) -> Dict:
    """
    Build a structured explanation of a single allocation decision.

    Combines attention weights (WHY districts were prioritised) with
    concrete allocation values (WHAT was decided) into a JSON object
    ready to be returned by the FastAPI router for GIS overlay.

    Parameters
    ----------
    state             : MDPState — current state before the decision.
    actions           : {district_name: {truck, uav}} — allocation decision.
    attention_weights : {district_name: float} — from AttentionPPOAgent.
    top_k             : int — number of top districts to highlight.

    Returns
    -------
    dict with the following structure::

        {
            "epoch": int,
            "cw_inventory_remaining": float,
            "top_districts": [
                {"district": str, "attention": float, "reason": str,
                 "truck_units": float, "uav_units": float}
            ],
            "summary": str
        }
    """
    total_allocated = sum(
        v["truck"] + v["uav"] for v in actions.values()
    )
    remaining = max(0.0, state.cw_inventory - total_allocated)

    top = top_k_districts(attention_weights, k=top_k)

    district_details = []
    for d_name, weight in top:
        # Find district state
        d_state = next((d for d in state.districts if d.name == d_name), None)
        alloc    = actions.get(d_name, {"truck": 0.0, "uav": 0.0})

        reason_parts = []
        if d_state:
            if d_state.deprivation_time >= 2:
                reason_parts.append(
                    f"{d_state.deprivation_time} consecutive periods in deprivation"
                )
            if d_state.shortage > 0:
                reason_parts.append(f"current shortage of {d_state.shortage:.0f} units")
            if d_state.demand_estimate > 0:
                reason_parts.append(
                    f"predicted demand of {d_state.demand_estimate:.0f} units"
                )
        reason = "; ".join(reason_parts) if reason_parts else "general risk assessment"

        district_details.append({
            "district":    d_name,
            "attention":   round(weight, 4),
            "reason":      reason,
            "truck_units": alloc["truck"],
            "uav_units":   alloc["uav"],
        })

    top_name = top[0][0] if top else "N/A"
    summary  = (
        f"At period {state.epoch}, the agent allocated {total_allocated:.0f} units total. "
        f"Primary focus: {top_name} (highest attention = {top[0][1]:.3f}). "
        f"Remaining CW inventory: {remaining:.0f} units."
        if top else
        f"At period {state.epoch}, no attention data available."
    )

    return {
        "epoch":                   state.epoch,
        "cw_inventory_remaining":  remaining,
        "top_districts":           district_details,
        "summary":                 summary,
    }


# ── Confidence Score ──────────────────────────────────────────────────────────

def decision_confidence(attention_weights: Dict[str, float]) -> float:
    """
    Compute a confidence score for the attention decision.

    Confidence is measured as the *concentration* of attention — a uniform
    distribution gives low confidence (0), while focusing all attention on
    one district gives high confidence (1).

    Uses the normalised max-attention ratio.

    Parameters
    ----------
    attention_weights : {district_name: weight}

    Returns
    -------
    float in [0, 1].
    """
    if not attention_weights:
        return 0.0
    weights = list(attention_weights.values())
    total   = sum(weights) + 1e-9
    max_w   = max(weights)
    n       = len(weights)
    # Uniform baseline = 1/n; concentration = max_w / (1/n * total)
    baseline    = total / n
    return min(1.0, float(max_w / (baseline + 1e-9)) / n)
