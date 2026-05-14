# reliefnet/backend/app/config.py
"""Application configuration using Pydantic Settings.
Reads from .env file located at project root.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Core settings
    mongo_uri: str = "mongodb://localhost:27017/"
    mongo_db: str = "reliefnet"
    log_level: str = "INFO"
    cors_origins: Optional[str] = "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174"
    
    # JWT
    jwt_secret_key: str = "change_this_to_a_random_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Paths
    data_export_dir: str = "../data/exports"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
