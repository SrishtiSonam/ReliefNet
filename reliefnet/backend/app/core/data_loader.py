# reliefnet/backend/app/core/data_loader.py
import argparse
import asyncio
import pandas as pd
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from ..config import Settings
from ..db.mongo import get_mongo_client, get_database
from ..db.indexes import create_indexes
from ..models.district import DistrictFeatures
from ..models.disaster import DisasterEvent
from ..models.road_network import RoadEdge

settings = Settings()

async def load_districts(db, export_dir: Path):
    path = export_dir / "reliefnet_district_features.csv"
    if not path.exists():
        print(f"Districts file not found: {path}")
        return
    
    df = pd.read_csv(path)
    # Convert to list of dicts and add 'location' for 2dsphere
    records = df.to_dict("records")
    for r in records:
        r["location"] = {
            "type": "Point",
            "coordinates": [r["longitude"], r["latitude"]]
        }
        
        # Inject defaults for missing fields to satisfy Pydantic
        defaults = {
            "lgd_code": "0", "population": 0.0, "area_sq_km": 0.0,
            "shelter_capacity_total": 0, "num_telecom_towers": 0, "road_length_km": 0.0,
            "num_bridges": 0, "has_airport": False, "has_railway": False,
            "river_proximity_km": 0.0, "coastal_district": False, "avg_elevation_m": 0.0,
            "nfhs_stunting_pct": 0.0, "nfhs_underweight_pct": 0.0, "nfhs_anemia_children": 0.0, "nfhs_institutional_birth": 0.0,
            "warehouse_rice_tons": 0.0, "warehouse_wheat_tons": 0.0, "warehouse_medicine_kits": 0, "warehouse_tarpaulin_units": 0,
            "hospital_density_per_1000sqkm": 0.0, "shelter_capacity_per_1000": 0.0, "telecom_density_per_100sqkm": 0.0,
            "flood_risk_score": 0.0, "health_vulnerability": 0.0, "warehouse_supply_per_capita": 0.0,
            "disaster_frequency": 0.0, "total_deaths_historical": 0.0, "total_affected_historical": 0.0, "total_damage_usd_historical": 0.0,
            "avg_recency_weight": 0.0, "network_degree": 0, "betweenness_centrality": 0.0, "max_road_failure_prob": 0.0,
            "is_isolated": False, "nearest_warehouse_km": 0.0, "vulnerability_score_pca": 0.0,
            "uav_reachable_within_range": False, "uav_terrain_penalty": 0.0, "truck_estimated_hours": 0.0,
            "truck_accessibility_score": 0.0, "disconnected_region_score": 0.0, "preferred_delivery_mode": "truck"
        }
        for k, v in defaults.items():
            if k not in r:
                r[k] = v

        # Validate with Pydantic
        DistrictFeatures(**r)
    
    # Bulk upsert
    for r in records:
        await db["districts"].update_one(
            {"district": r["district"]},
            {"$set": r},
            upsert=True
        )
    print(f"Loaded {len(records)} districts.")

async def load_disasters(db, export_dir: Path):
    path = export_dir / "reliefnet_disasters.csv"
    if not path.exists():
        print(f"Disasters file not found: {path}")
        return
    
    df = pd.read_csv(path)
    records = df.to_dict("records")
    for r in records:
        r["location"] = {
            "type": "Point",
            "coordinates": [r["longitude"], r["latitude"]]
        }
        # Handle NaN values which Pydantic might complain about
        for k, v in r.items():
            if pd.isna(v):
                r[k] = 0.0 if isinstance(v, float) else ""
        
        DisasterEvent(**r)
    
    for r in records:
        await db["disasters"].update_one(
            {"dis_no": r["dis_no"]},
            {"$set": r},
            upsert=True
        )
    print(f"Loaded {len(records)} disasters.")

async def load_road_network(db, export_dir: Path):
    path = export_dir / "reliefnet_road_network.csv"
    if not path.exists():
        print(f"Road edges file not found: {path}")
        return
    
    df = pd.read_csv(path)
    records = df.to_dict("records")
    for r in records:
        # Inject defaults for missing fields to satisfy Pydantic
        defaults = {
            "flood_risk": 0.0,
            "landslide_risk": 0.0,
            "failure_probability": 0.0
        }
        for k, v in defaults.items():
            if k not in r:
                r[k] = v
        
        RoadEdge(**r)
    
    for r in records:
        await db["road_network"].update_one(
            {"source": r["source"], "target": r["target"]},
            {"$set": r},
            upsert=True
        )
    print(f"Loaded {len(records)} road edges.")

async def main():
    parser = argparse.ArgumentParser(description="Load ReliefNet data from CSV exports to MongoDB.")
    parser.add_argument("--export-dir", type=str, default="../data/exports", help="Path to data/exports directory")
    args = parser.parse_args()
    
    export_dir = Path(args.export_dir).resolve()
    client = await get_mongo_client(settings.mongo_uri)
    db = get_database(client, settings.mongo_db)
    
    print("Ensuring indexes...")
    await create_indexes(db)
    
    print(f"Loading data from {export_dir}...")
    await load_districts(db, export_dir)
    await load_disasters(db, export_dir)
    await load_road_network(db, export_dir)
    
    client.close()
    print("Data loading complete.")

if __name__ == "__main__":
    asyncio.run(main())
