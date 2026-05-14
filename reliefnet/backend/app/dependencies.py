# reliefnet/backend/app/dependencies.py
"""FastAPI dependency utilities.
Provides a dependency that yields the Motor database from app.state.
"""

from fastapi import Depends, Request
from .config import Settings

# Settings instance (singleton)
settings = Settings()

async def db_dep(request: Request):
    """Dependency that returns the shared Motor database from app.state."""
    return request.app.state.mongo_client[settings.mongo_db]
