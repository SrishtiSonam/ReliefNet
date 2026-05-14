# reliefnet/backend/app/api/v1/router.py
from fastapi import APIRouter
from . import auth, districts, warehouses, disasters, simulation, forecasting, allocation, explainability, requests

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(districts.router, prefix="/districts", tags=["districts"])
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(disasters.router, prefix="/disasters", tags=["disasters"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
api_router.include_router(forecasting.router, prefix="/forecast", tags=["forecast"])
api_router.include_router(allocation.router, prefix="/allocation", tags=["allocation"])
api_router.include_router(explainability.router, prefix="/explain", tags=["explain"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
