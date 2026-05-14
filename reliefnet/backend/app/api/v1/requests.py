from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
import uuid
from ...dependencies import db_dep

router = APIRouter()

class CitizenRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    contact: str
    need_type: str
    address: str
    people_affected: int
    urgency: str
    description: str
    status: str = "PENDING"
    created_at: datetime = Field(default_factory=datetime.utcnow)

@router.post("/", response_model=CitizenRequest)
async def create_request(req: dict, db = Depends(db_dep)):
    new_req = CitizenRequest(**req)
    await db.get_collection("requests").insert_one(new_req.model_dump())
    return new_req

@router.get("/", response_model=List[CitizenRequest])
async def get_requests(db = Depends(db_dep)):
    docs = await db.get_collection("requests").find().sort("created_at", -1).to_list(500)
    return [CitizenRequest(**doc) for doc in docs]

@router.put("/{request_id}/status")
async def update_status(request_id: str, status: str, db = Depends(db_dep)):
    await db.get_collection("requests").update_one(
        {"request_id": request_id}, {"$set": {"status": status}}
    )
    return {"status": "updated"}
