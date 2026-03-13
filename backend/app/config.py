# ─── config.py ───────────────────────────────────────────────────────────────
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB:  str = "flood_relief_india"
    SECRET_KEY: str = "flood-relief-secret"

    class Config:
        env_file = ".env"

settings = Settings()
