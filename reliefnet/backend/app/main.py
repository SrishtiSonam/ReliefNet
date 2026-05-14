# reliefnet/backend/app/main.py
"""FastAPI application entry point.
Includes CORS configuration, lifespan event for MongoDB connection, and a simple health check.
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to sys.path to allow absolute imports of ml_services
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from .config import Settings
from .logging_config import configure_logging
from .db.mongo import get_mongo_client
from .db.indexes import create_indexes
from .api.v1.router import api_router

# Load settings (reads .env automatically)
settings = Settings()

# Configure logging early
configure_logging(settings.log_level)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MongoDB connection lifecycle."""
    # Startup: connect to MongoDB
    app.state.mongo_client = await get_mongo_client(settings.mongo_uri)
    await create_indexes(app.state.mongo_client[settings.mongo_db])
    yield
    # Shutdown: close MongoDB connection
    app.state.mongo_client.close()

app = FastAPI(
    title="ReliefNet Backend",
    description="FastAPI backend for ReliefNet disaster management platform",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS - allow frontend dev server (default from env or localhost)
origins = [origin.strip() for origin in settings.cors_origins.split(",")] if settings.cors_origins else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health check endpoint
@app.get("/health", response_class=JSONResponse)
async def health_check():
    return {"status": "ok", "message": "ReliefNet backend is running"}

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")
