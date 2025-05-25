# core/config.py

"""
Application configuration constants.
Everything is hard-coded for PRODUCTION deployment.
"""

from types import SimpleNamespace

# -----------------------------------------------------------------------------
# Environment & Debug
# -----------------------------------------------------------------------------
ENV = "PRODUCTION"
DEBUG = False

# -----------------------------------------------------------------------------
# Security / Auth
# -----------------------------------------------------------------------------
# Only needed if you verify tokens server-side:
CLERK_API_KEY = ""          # (optional backend-only key)
CLERK_FRONTEND_API = ""     # your Clerk publishable key
CLERK_JWKS_URL = "https://loving-gopher-42.clerk.accounts.dev/.well-known/jwks.json"

CLERK_ISSUER = "https://loving-gopher-42.clerk.accounts.dev"
CLERK_AUDIENCE = "authenticated"

# -----------------------------------------------------------------------------
# Database & Redis (force SSL/TLS)
# -----------------------------------------------------------------------------
DATABASE_URL ="postgresql://postgres.bilwoyqidotwddxgdmga:AWZ7qSFrB4WRop55@aws-0-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require"
REDIS_URL ="rediss://:AVkDAAIjcDFiNzgzYzY4YmFlMDY0NThiYmZiNTY1MGVhOWY0NjI5ZnAxMA@social-guppy-22787.upstash.io:6379/0"

# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
# List all allowed origins here:
BACKEND_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://statuspage-frontend.vercel.app",
]

# -----------------------------------------------------------------------------
# Export a single global settings object
# -----------------------------------------------------------------------------
settings = SimpleNamespace(
    ENV=ENV,
    DEBUG=DEBUG,
    DATABASE_URL=DATABASE_URL,
    REDIS_URL=REDIS_URL,
    BACKEND_CORS_ORIGINS=BACKEND_CORS_ORIGINS,
    CLERK_API_KEY=CLERK_API_KEY,
    CLERK_FRONTEND_API=CLERK_FRONTEND_API,
    CLERK_JWKS_URL=CLERK_JWKS_URL,
    CLERK_ISSUER=CLERK_ISSUER,
    CLERK_AUDIENCE=CLERK_AUDIENCE,
)