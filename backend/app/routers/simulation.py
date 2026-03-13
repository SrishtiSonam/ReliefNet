# ─── routers/simulation.py ────────────────────────────────────────────────────
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.models.simulation import SimulationConfig, SimulationRun
from app.database import get_db
from app.ml.mdp import MDPState, DistrictState, ScenarioGenerator
from app.ml.dl_vfa import DLVFA
from app.ml.nn_vfa import NNVFA, RuleBasedHeuristic
from app.ml.ppo import PPOAgent
from app.data.demand_estimator import estimate_demand
from app.data.cost_calculator import compute_costs
from app.data.scenario_gen import build_scenario_generator
from datetime import datetime
import asyncio

router_sim = APIRouter()

@router_sim.post("/run")
async def run_simulation(config: SimulationConfig, bg: BackgroundTasks):
    db   = get_db()
    run  = {"config": config.dict(), "status": "pending",
            "created_at": datetime.utcnow().isoformat(), "results": []}
    res  = await db.simulations.insert_one(run)
    sim_id = str(res.inserted_id)
    bg.add_task(_run_simulation_task, sim_id, config)
    return {"simulation_id": sim_id, "status": "pending"}

async def _run_simulation_task(sim_id: str, config: SimulationConfig):
    db = get_db()
    await db.simulations.update_one({"_id": sim_id}, {"$set": {"status": "running"}})
    try:
        # Build district states
        districts = []
        for dname in config.selected_districts:
            demand = await estimate_demand(dname, config.period_hours)
            # Default coords — ideally fetched from metadata
            d = DistrictState(
                name            = dname,
                inventory       = 0.0,
                shortage        = 0.0,
                deprivation_time= 0,
                demand_estimate = demand["demand_mean"],
                demand_std      = demand["demand_std"],
                uav_cost        = 500.0,   # Default, computed by cost_calculator
                truck_cost      = 2000.0
            )
            districts.append(d)

        supply_mean = sum(d.demand_estimate for d in districts)
        init_state  = MDPState(epoch=0, cw_inventory=supply_mean * 2, districts=districts)
        scen_gen    = await build_scenario_generator(districts, supply_mean, config.n_periods)

        results = []
        for method in config.methods:
            if method == "dl_vfa":
                agent = DLVFA(districts, config.n_periods,
                               config.truck_capacity, config.uav_capacity)
                agent.train(scen_gen, init_state, config.n_training_episodes)
                r = agent.evaluate(scen_gen, init_state)
            elif method == "nn_vfa":
                agent = NNVFA(districts, config.n_periods,
                               config.truck_capacity, config.uav_capacity)
                agent.train(scen_gen, init_state, config.n_training_episodes)
                r = agent.evaluate(scen_gen, init_state)
            elif method == "ppo":
                agent = PPOAgent(districts, config.n_periods,
                                  config.truck_capacity, config.uav_capacity)
                agent.train(scen_gen, init_state, min(config.n_training_episodes, 5000))
                r = agent.evaluate(scen_gen, init_state)
            elif method == "rule_based":
                agent = RuleBasedHeuristic(districts, config.n_periods,
                                            config.truck_capacity, config.uav_capacity)
                r = agent.evaluate(scen_gen, init_state)
            else:
                continue
            results.append(r)

        await db.simulations.update_one(
            {"_id": sim_id},
            {"$set": {"status": "completed", "results": results}}
        )
    except Exception as e:
        await db.simulations.update_one(
            {"_id": sim_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )

@router_sim.get("/{sim_id}")
async def get_simulation(sim_id: str):
    db  = get_db()
    doc = await db.simulations.find_one({"_id": sim_id})
    if not doc:
        raise HTTPException(404, "Simulation not found")
    doc["_id"] = str(doc["_id"])
    return doc

@router_sim.get("/")
async def list_simulations():
    db   = get_db()
    docs = await db.simulations.find({}, {"_id": 1, "config.name": 1,
                                           "status": 1, "created_at": 1}
                                     ).to_list(length=50)
    for d in docs:
        d["_id"] = str(d["_id"])
    return {"simulations": docs}
