# reliefnet/backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ...core.auth.jwt_handler import create_access_token, get_password_hash, verify_password
from ...db.repositories.user_repo import UserRepository
from ...dependencies import db_dep
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "COORDINATOR"

@router.post("/register")
async def register(user_in: UserCreate, db = Depends(db_dep)):
    repo = UserRepository(db)
    # Check if user exists
    existing = await repo.get_by_username(user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password
    user_dict = user_in.model_dump()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    
    await repo.create(user_dict)
    return {"message": "User created successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(db_dep)):
    repo = UserRepository(db)
    user = await repo.get_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"], "role": user.get("role", "USER")})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role": user.get("role", "USER")
        }
    }
