# reliefnet/backend/app/api/v1/explainability.py
from fastapi import APIRouter, Depends, HTTPException
from ...dependencies import db_dep
from ...db.repositories.district_repo import DistrictRepository
from ...core.explainability.service import explain_vulnerability

router = APIRouter()

@router.get("/district/{name}")
async def explain_district(name: str, db = Depends(db_dep)):
    repo = DistrictRepository(db)
    district = await repo.get_by_name(name)
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    return explain_vulnerability(district)
