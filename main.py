import logging
import asyncio
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis

from dotenv import load_dotenv
from core.config import settings
from db.init_db import init_db
from api.routes import (
    health_router,
    services_router,
    organization_router,
    team_router,
    incident_router,
    users_router,
    public_router,
)

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

# CORS (note: CORS middleware does not apply to WS handshakes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals for Redis and connected WebSockets
redis_client: redis.Redis | None = None
connected_websockets: list[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize DB, Redis, and start the listener task."""
    init_db()
    logger.info("Database initialized")

    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

    # Fire-and-forget the Redis Pub/Sub listener
    asyncio.create_task(_redis_listener())


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up Redis on shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """
    Accept a client WebSocket, keep it open until they disconnect,
    and remove from our list on disconnect.
    """
    await ws.accept()
    connected_websockets.append(ws)
    logger.info(f"WebSocket client connected: {ws.client}")

    try:
        # Keep the connection alive indefinitely
        while True:
            # We don't actually expect clients to send anything;
            # this just waits until they disconnect.
            await ws.receive_text()
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {ws.client}")
    except Exception as e:
        logger.error(f"WebSocket error with {ws.client}: {e}")
    finally:
        # Ensure removal even on unexpected errors
        if ws in connected_websockets:
            connected_websockets.remove(ws)


async def _redis_listener():
    """
    Listen on the Redis "status_updates" channel and broadcast
    every incoming message to all connected WebSocket clients.
    """
    if not redis_client:
        logger.error("Redis client not initialized; listener exiting.")
        return

    pubsub = redis_client.pubsub()
    await pubsub.subscribe("status_updates")
    logger.info("Subscribed to Redis channel: status_updates")

    async for msg in pubsub.listen():
        if msg.get("type") == "message":
            try:
                payload = json.loads(msg["data"])
            except Exception as e:
                logger.error(f"Invalid JSON in Redis message: {e}")
                continue

            # Broadcast to every live client
            for ws in connected_websockets.copy():
                try:
                    await ws.send_json(payload)
                except Exception:
                    # If send fails, remove that socket
                    connected_websockets.remove(ws)
                    logger.info(f"Removed dead WebSocket: {ws.client}")


# Finally: include all your routers
app.include_router(health_router)
app.include_router(services_router)
app.include_router(organization_router)
app.include_router(team_router)
app.include_router(incident_router)
app.include_router(users_router)
app.include_router(public_router)
