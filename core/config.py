# core/config.py

"""
Application configuration constants.
Everything is hard-coded for PRODUCTION deployment.
"""

# -----------------------------------------------------------------------------
# Environment & Debug
# -----------------------------------------------------------------------------
ENV = "PRODUCTION"
DEBUG = False

# -----------------------------------------------------------------------------
# Security / Auth
# -----------------------------------------------------------------------------
# A long random string—keep this secret!
SECRET_KEY = "your-generated-secret-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# -----------------------------------------------------------------------------
# Database & Redis
# -----------------------------------------------------------------------------
# Supabase Postgres (force SSL)
DATABASE_URL = (
    "postgresql://postgres:AWZ7qSFrB4WRop55"
    "@db.bilwoyqidotwddxgdmga.supabase.co:5432/postgres"
    "?sslmode=require"
)

# Upstash Redis over TLS
REDIS_URL = (
    "rediss://:AVkDAAIjcDFiNzgzYzY4YmFlMDY0NThiYmZiNTY1MGVhOWY0NjI5ZnAxMA"
    "@social-guppy-22787.upstash.io:6379/0"
)

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
# Clerk (Auth) settings
# -----------------------------------------------------------------------------
# (Only needed if you verify tokens server-side)
CLERK_API_KEY = ""          # (optional backend-only key)
CLERK_FRONTEND_API = ""     # your Clerk publishable key

CLERK_JWKS_URL = (
    "https://loving-gopher-42.clerk.accounts.dev/.well-known/jwks.json"
)
CLERK_ISSUER = "https://loving-gopher-42.clerk.accounts.dev"
CLERK_AUDIENCE = "authenticated"
