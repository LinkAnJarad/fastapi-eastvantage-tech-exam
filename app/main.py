import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import Base, engine
from app.routers import addresses

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Lifespan manager to handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create db tables in SQLite if they don't exist
    logger.info("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)

    logger.info("Starting up FastAPI application...")
    yield

    # Shutdown event
    logger.info("Shutting down FastAPI application...")

# FastAPI main app
app = FastAPI(
    title="Address Book API Minimal",
    description="A minimal FastAPI application for managing addresses + Haversine distance calculations.",
    version="0.0.1",
    lifespan=lifespan
)

# Mount routers
app.include_router(addresses.router)



# Simple health check endpoint
@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint to verify that the API is running.
    """
    logger.info("Health check endpoint called.")
    return {"status": "ok", "message": "Address Book API is running."}