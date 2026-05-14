# reliefnet/backend/app/core/explainability/service.py
from typing import Dict, Any
from ...models.district import DistrictFeatures

def explain_vulnerability(district: DistrictFeatures) -> Dict[str, Any]:
    """
    Provides a breakdown of the vulnerability score for a district.
    Explains the top contributors to its risk level.
    """
    # These weights should match the ones used in feature engineering (Notebook 01)
    components = {
        "Flood Exposure": district.flood_risk_score * 0.3,
        "Health Vulnerability": district.health_vulnerability * 0.3,
        "Historical Disaster Damage": district.historical_damage_score * 0.2,
        "Transport Isolation": (1 - district.transport_accessibility) * 0.2
    }
    
    # Normalize to percentages for the UI
    total = sum(components.values())
    if total == 0:
        breakdown = {k: 0 for k in components}
    else:
        breakdown = {k: round((v / total) * 100, 1) for k, v in components.items()}
    
    # Generate a natural language summary
    top_factor = max(components, key=components.get)
    summary = f"The primary driver of risk in {district.district} is {top_factor}."
    
    if district.vulnerability_tier == "CRITICAL":
        summary += " Immediate infrastructure reinforcement is recommended."
    
    return {
        "district": district.district,
        "vulnerability_score": district.vulnerability_score,
        "vulnerability_tier": district.vulnerability_tier,
        "top_contributor": top_factor,
        "breakdown_pct": breakdown,
        "summary": summary
    }
