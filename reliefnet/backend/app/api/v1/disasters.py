# reliefnet/backend/app/api/v1/disasters.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ...db.repositories.disaster_repo import DisasterRepository
from ...dependencies import db_dep
from ...models.disaster import DisasterEvent

router = APIRouter()

@router.get("/", response_model=List[DisasterEvent])
async def get_disasters(
    type: Optional[str] = None,
    season: Optional[str] = None,
    district: Optional[str] = None,
    db = Depends(db_dep)
):
    repo = DisasterRepository(db)
    query = {}
    if type:
        query["disaster_type"] = type
    if season:
        query["season"] = season
    if district:
        query["district"] = district
    return await repo.get_many(query=query)

@router.get("/stats/by-type")
async def get_disaster_stats_by_type(db = Depends(db_dep)):
    pipeline = [
        {"$group": {"_id": "$disaster_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    cursor = db["disasters"].aggregate(pipeline)
    results = []
    async for doc in cursor:
        results.append(doc)
    return results
