# reliefnet/backend/app/core/simulation/flood_model.py
from ...models.district import DistrictFeatures

def calculate_flood_damage(district: DistrictFeatures, intensity: float) -> float:
    """Calculate a damage score [0-1] based on disaster intensity and district vulnerability."""
    # Base vulnerability
    vuln = district.vulnerability_score
    
    # Flood specific risk factors
    flood_factor = district.flood_risk_score
    elevation_factor = 1 - (min(district.avg_elevation_m, 1000) / 1000) # Lower elevation = higher risk
    coastal_factor = 1.2 if district.coastal_district else 1.0
    
    # Combined damage score
    damage = intensity * (vuln * 0.4 + flood_factor * 0.4 + elevation_factor * 0.2) * coastal_factor
    
    return min(max(damage, 0.0), 1.0)
