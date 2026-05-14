# reliefnet/backend/app/core/simulation/shortage_estimator.py
from ...models.district import DistrictFeatures

def estimate_shortages(district: DistrictFeatures, damage_score: float) -> dict:
    """Estimate material shortages based on district population and damage intensity."""
    # Assume 10% of population is affected per 0.1 damage_score
    affected_pop = district.population * (damage_score)
    
    # Needs per person (conservative estimates)
    # 500g rice/day, 500g wheat/day, 1 med kit per 100 people, 1 tarpaulin per 5 people
    return {
        "rice": (affected_pop * 0.0005) * 7, # 7 days supply in tons
        "wheat": (affected_pop * 0.0005) * 7,
        "medicine": int(affected_pop / 100),
        "tarpaulin": int(affected_pop / 5)
    }
