from fastapi import FastAPI
from routes import health_router
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import redis

if os.getenv("ENV") != "production":
    load_dotenv(dotenv_path=".env.local", override=True)

POSTGRESQL_USER = os.getenv("POSTGRESQL_USER")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD")
POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST")
POSTGRESQL_PORT = os.getenv("POSTGRESQL_PORT")
POSTGRESQL_DBNAME = os.getenv("POSTGRESQL_DBNAME")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# DATABASE_URL = f"postgresql+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DBNAME}?sslmode=require"
DATABASE_URL = f"postgresql+psycopg2://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DBNAME}"
engine = create_engine(DATABASE_URL)

try:
    redisClient = redis.Redis(
        host=REDIS_HOST,
        port=int(REDIS_PORT),
        password=REDIS_PASSWORD,
        # ssl=True
    )
    print("Connected to Redis")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")

app = FastAPI()

app.include_router(health_router)