"""
main.py  — Updated entry point
Registers all original + new routers for B.2, B.5, B.6, B.7, B.12.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import districts, flood_events, simulation, allocation, data_ingestion
from app.routers.ml_extensions import router_ml
from app.routers.auth import router as router_auth
from app.database import connect_db, disconnect_db
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title       = "Flood Relief India — AI Engine",
    description = (
        "Stochastic Dynamic Post-Flood Inventory Allocation for India.\n\n"
        "Improvements: RF Demand Model · MIP Solver · Multi-Commodity · "
        "Multi-Depot · LSTM Flood Predictor · GIS Map · JWT Auth"
    ),
    version     = "2.0.0",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["http://localhost:3000", "http://localhost:5000"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ─── Original routers ─────────────────────────────────────────────────────────
app.include_router(districts.router,      prefix="/api/districts",    tags=["Districts"])
app.include_router(flood_events.router,   prefix="/api/flood-events", tags=["Flood Events"])
app.include_router(simulation.router,     prefix="/api/simulation",   tags=["Simulation"])
app.include_router(allocation.router,     prefix="/api/allocation",   tags=["Allocation"])
app.include_router(data_ingestion.router, prefix="/api/data",         tags=["Data Ingestion"])

# ─── New routers (B.2, B.5, B.6, B.7) ────────────────────────────────────────
app.include_router(router_ml,   prefix="/api/ml",   tags=["ML Extensions"])

# ─── Auth router (B.12) ───────────────────────────────────────────────────────
app.include_router(router_auth, prefix="/api/auth", tags=["Authentication"])

# ─── Lifecycle ────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await connect_db()
    logger.info("FastAPI v2.0 started. MongoDB connected.")

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()
    logger.info("FastAPI shutdown. MongoDB disconnected.")

@app.get("/")
def root():
    return {
        "message": "Flood Relief India AI Engine v2.0 is running.",
        "new_features": [
            "B.2 — Random Forest Demand Estimator",
            "B.3 — PuLP MIP Allocation Solver",
            "B.5 — Multi-Commodity Relief (food/water/medicine/shelter)",
            "B.6 — Multi-Depot Warehouses (state capitals + post offices)",
            "B.7 — LSTM Flood Prediction (3–7 days ahead)",
            "B.8 — GIS Interactive Map (React + Leaflet)",
            "B.12 — JWT Authentication + PDF Export",
        ],
    }