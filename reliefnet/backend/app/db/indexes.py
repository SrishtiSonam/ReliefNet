# reliefnet/backend/app/db/indexes.py
"""MongoDB collection index definitions for all 11 collections.
Run at startup to ensure performant queries.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

async def create_indexes(db: AsyncIOMotorDatabase):
    # districts collection
    await db["districts"].create_index([("district", 1)], unique=True)
    await db["districts"].create_index([("state", 1)])
    await db["districts"].create_index([("location", "2dsphere")])
    await db["districts"].create_index([("vulnerability_score", -1)])

    # warehouses collection
    await db["warehouses"].create_index([("warehouse_id", 1)], unique=True)
    await db["warehouses"].create_index([("district", 1)])
    await db["warehouses"].create_index([("location", "2dsphere")])

    # shelters collection
    await db["shelters"].create_index([("shelter_id", 1)], unique=True)
    await db["shelters"].create_index([("district", 1)])
    await db["shelters"].create_index([("location", "2dsphere")])

    # hospitals collection
    await db["hospitals"].create_index([("hospital_id", 1)], unique=True)
    await db["hospitals"].create_index([("district", 1)])
    await db["hospitals"].create_index([("location", "2dsphere")])

    # disasters collection
    await db["disasters"].create_index([("dis_no", 1)], unique=True)
    await db["disasters"].create_index([("year", 1)])
    await db["disasters"].create_index([("disaster_type", 1)])
    await db["disasters"].create_index([("location", "2dsphere")])

    # road_network collection
    await db["road_network"].create_index([("source", 1), ("target", 1)], unique=True)
    await db["road_network"].create_index([("failure_probability", -1)])

    # simulation_runs collection
    await db["simulation_runs"].create_index([("run_id", 1)], unique=True)
    await db["simulation_runs"].create_index([("created_at", -1)])
    await db["simulation_runs"].create_index([("status", 1)])

    # forecasts collection
    await db["forecasts"].create_index([("forecast_id", 1)], unique=True)
    await db["forecasts"].create_index([("district", 1)])
    await db["forecasts"].create_index([("model_type", 1)])
    await db["forecasts"].create_index([("created_at", -1)])

    # allocations collection
    await db["allocations"].create_index([("allocation_id", 1)], unique=True)
    await db["allocations"].create_index([("simulation_run_id", 1)])
    await db["allocations"].create_index([("district", 1)])

    # users collection
    await db["users"].create_index([("email", 1)], unique=True)
    await db["users"].create_index([("role", 1)])

    # overrides collection
    await db["overrides"].create_index([("override_id", 1)], unique=True)
    await db["overrides"].create_index([("allocation_id", 1)])
    await db["overrides"].create_index([("user_id", 1)])
    
    logger.info("[OK] All MongoDB indexes created successfully.")
