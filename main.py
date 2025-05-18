import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from core.config import settings
from db.init_db import init_db

from api.routes import health_router, services_router, organization_router, team_router
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local", override=True)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Status Page API",
    description="API for the Status Page application",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis client
redis_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on app startup."""
    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Initialize Redis client
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on app shutdown."""
    # Close Redis connection
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")

app.include_router(health_router)
app.include_router(services_router)
app.include_router(organization_router)
app.include_router(team_router)

# Import and include API routes
# from app.api.routes import auth, organizations, teams, services, incidents, public
# app.include_router(auth.router, prefix=settings.API_V1_STR)
# app.include_router(organizations.router, prefix=settings.API_V1_STR)
# app.include_router(teams.router, prefix=settings.API_V1_STR)
# app.include_router(services.router, prefix=settings.API_V1_STR)
# app.include_router(incidents.router, prefix=settings.API_V1_STR)
# app.include_router(public.router, prefix=settings.API_V1_STR)

# Uncomment the above imports and app.include_router calls when you implement the routes