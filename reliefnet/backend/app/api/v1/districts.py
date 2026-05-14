# reliefnet/backend/app/api/v1/districts.py
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from ...db.repositories.district_repo import DistrictRepository
from ...dependencies import db_dep
from ...models.district import DistrictFeatures

router = APIRouter()

@router.get("/", response_model=List[DistrictFeatures])
async def get_districts(
    state: Optional[str] = None,
    tier: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db = Depends(db_dep)
):
    repo = DistrictRepository(db)
    query = {}
    if state:
        query["state"] = state
    if tier:
        query["vulnerability_tier"] = tier
    
    skip = (page - 1) * limit
    return await repo.get_many(query=query, limit=limit, skip=skip)

@router.get("/near", response_model=List[DistrictFeatures])
async def get_nearby_districts(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(100),
    db = Depends(db_dep)
):
    """Find districts within a specific radius of a coordinate."""
    # Using a simple box query for simplicity in this version
    # Real spatial queries use $near or $geoWithin in MongoDB
    repo = DistrictRepository(db)
    all_districts = await repo.get_many(limit=1000)
    
    results = []
    for d in all_districts:
        dist = calculate_distance(lat, lon, d.latitude, d.longitude)
        if dist <= radius_km:
            results.append(d)
    return results

@router.get("/{name}", response_model=DistrictFeatures)
async def get_district(name: str, db = Depends(db_dep)):
    repo = DistrictRepository(db)
    district = await repo.get_by_name(name)
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    return district

def calculate_distance(lat1, lon1, lat2, lon2):
    import math
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c
