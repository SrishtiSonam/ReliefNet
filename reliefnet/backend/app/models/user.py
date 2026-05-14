# reliefnet/backend/app/models/user.py
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: str = "COORDINATOR"  # ADMIN|COORDINATOR|VIEWER
    hashed_password: str
    is_active: bool = True
