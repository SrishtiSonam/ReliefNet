# reliefnet/backend/app/core/simulation/engine.py
import math
import uuid
import os
from datetime import datetime
from typing import List
from pathlib import Path

from ...models.simulation import SimulationRequest, SimulationResult, AffectedDistrict
from .flood_model import calculate_flood_damage
from ml_services.forecasting.xgboost_service import DemandForecaster
from ...db.repositories.district_repo import DistrictRepository

# Initialize ML Forecaster (load model if exists)
MODEL_PATH = Path(__file__).resolve().parents[4] / "ml_services" / "models" / "demand_forecaster.json"
forecaster = DemandForecaster(model_path=str(MODEL_PATH) if MODEL_PATH.exists() else None)

async def run_disaster_simulation(request: SimulationRequest, db) -> SimulationResult:
    """Run a full disaster simulation using ML-based impact assessment."""
    repo = DistrictRepository(db)
    all_districts = await repo.get_many(limit=1000)
    
    affected_districts: List[AffectedDistrict] = []
    
    for district in all_districts:
        dist = calculate_distance(
            request.center_lat, request.center_lon,
            district.latitude, district.longitude
        )
        
        if dist <= request.impact_radius_km:
            intensity = request.severity * (1 - (dist / request.impact_radius_km))
            damage_score = calculate_flood_damage(district, intensity)
            
            # --- ML INTEGRATION ---
            # Use XGBoost forecaster to predict demand surge
            # We treat the damage_score as an input to the demand prediction
            ml_prediction = forecaster.predict(district.model_dump(), horizon_days=7)
            demand_multiplier = damage_score * 10
            
            affected_districts.append(AffectedDistrict(
                district=district.district,
                estimated_damage_score=damage_score,
                estimated_shortage_rice_tons=ml_prediction[0] * demand_multiplier,
                estimated_shortage_wheat_tons=ml_prediction[1] * demand_multiplier,
                estimated_shortage_medicine_kits=int(ml_prediction[2] * demand_multiplier * 10),
                estimated_shortage_tarpaulin_units=int(ml_prediction[3] * demand_multiplier * 100),
                accessibility_score=district.transport_accessibility * (1 - district.avg_road_failure_prob * intensity)
            ))
            
    return SimulationResult(
        run_id=str(uuid.uuid4()),
        created_at=datetime.utcnow(),
        request=request,
        affected_districts=affected_districts,
        status="COMPLETED"
    )

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
