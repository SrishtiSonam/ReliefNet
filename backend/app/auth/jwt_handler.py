"""
auth/jwt_handler.py  (B.12)
JWT token generation, validation, and password hashing utilities.

Uses:
    - python-jose  for JWT signing (RS256 / HS256)
    - passlib      for bcrypt password hashing
    - fastapi      for dependency injection

Token payload schema:
    {
      "sub":   "<user_id>",
      "email": "<email>",
      "role":  "admin" | "manager" | "viewer",
      "exp":   <unix_timestamp>
    }
"""

from datetime import datetime, timedelta
from typing import Optional, Dict

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

# ─── Configuration ────────────────────────────────────────────────────────────
ALGORITHM         = "HS256"
ACCESS_TOKEN_EXP  = timedelta(hours=8)
REFRESH_TOKEN_EXP = timedelta(days=7)

pwd_context    = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme  = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ─── Password utilities ───────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ─── Token creation ───────────────────────────────────────────────────────────
def create_access_token(data: Dict,
                         expires_delta: timedelta = ACCESS_TOKEN_EXP) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + expires_delta
    payload["iat"] = datetime.utcnow()
    payload["type"] = "access"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict) -> str:
    payload = data.copy()
    payload["exp"]  = datetime.utcnow() + REFRESH_TOKEN_EXP
    payload["type"] = "refresh"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


# ─── Token decoding ───────────────────────────────────────────────────────────
def decode_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── FastAPI dependency ───────────────────────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Dependency: validate JWT, return decoded user payload.
    Usage:  current_user: dict = Depends(get_current_user)
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Expected access token.")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token missing 'sub' claim.")
    return payload


async def require_admin(current: Dict = Depends(get_current_user)) -> Dict:
    """Dependency: current user must have role='admin'."""
    if current.get("role") != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required.")
    return current


async def require_manager_or_above(current: Dict = Depends(get_current_user)) -> Dict:
    """Dependency: role must be 'admin' or 'manager'."""
    if current.get("role") not in ("admin", "manager"):
        raise HTTPException(status.HTTP_403_FORBIDDEN,
                            "Manager or Admin access required.")
    return current