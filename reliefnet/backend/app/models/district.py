# reliefnet/backend/app/models/district.py
from pydantic import BaseModel, Field
from typing import Optional
from .common import GeoLocation

class DistrictFeatures(BaseModel):
    # Identity
    district: str
    state: str
    lgd_code: str
    latitude: float
    longitude: float
    location: Optional[GeoLocation] = None

    # Raw Infrastructure
    population: float
    area_sq_km: float
    num_hospitals: int
    num_warehouses: int
    num_shelters: int
    shelter_capacity_total: int
    num_telecom_towers: int
    road_length_km: float
    num_bridges: int
    has_airport: bool
    has_railway: bool
    river_proximity_km: float
    coastal_district: bool
    avg_elevation_m: float

    # NFHS-5 Health
    nfhs_stunting_pct: float
    nfhs_underweight_pct: float
    nfhs_anemia_children: float
    nfhs_institutional_birth: float

    # Warehouse Stock
    warehouse_rice_tons: float
    warehouse_wheat_tons: float
    warehouse_medicine_kits: int
    warehouse_tarpaulin_units: int

    # Engineered — Density/Access
    population_density: float
    hospital_density_per_1000sqkm: float
    shelter_capacity_per_1000: float
    telecom_density_per_100sqkm: float
    transport_accessibility: float

    # Engineered — Risk
    flood_risk_score: float
    health_vulnerability: float
    warehouse_supply_per_capita: float

    # Engineered — Historical
    disaster_frequency: float
    total_deaths_historical: float
    total_affected_historical: float
    total_damage_usd_historical: float
    historical_damage_score: float
    avg_recency_weight: float

    # Engineered — Road Network
    network_degree: int
    betweenness_centrality: float
    avg_road_failure_prob: float
    max_road_failure_prob: float
    is_isolated: bool

    # Engineered — Spatial
    nearest_warehouse_km: float

    # Vulnerability Index
    vulnerability_score: float
    vulnerability_score_pca: float
    vulnerability_tier: str  # LOW|MEDIUM|HIGH|CRITICAL

    # UAV & Logistics
    uav_reachable_within_range: bool
    uav_terrain_penalty: float
    truck_estimated_hours: float
    truck_accessibility_score: float
    disconnected_region_score: float
    preferred_delivery_mode: str # truck|uav|both|emergency_airlift
