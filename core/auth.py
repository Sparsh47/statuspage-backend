from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
import httpx
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local", override=True)

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "https://your-clerk-domain/.well-known/jwks.json")
CLERK_ISSUER = os.getenv("CLERK_ISSUER", "https://your-clerk-domain")
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE", "authenticated")

# Cache for keys
_jwk_cache = {}

async def get_public_key(kid: str):
    if kid in _jwk_cache:
        return _jwk_cache[kid]

    async with httpx.AsyncClient() as client:
        resp = await client.get(CLERK_JWKS_URL)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch JWKS from Clerk")
        keys = resp.json()["keys"]

    for key in keys:
        if key["kid"] == kid:
            _jwk_cache[kid] = key
            return key

    raise HTTPException(status_code=401, detail="Invalid token key ID")

async def verify_clerk_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    try:
        unverified_header = jwt.get_unverified_header(token)
        key = await get_public_key(unverified_header["kid"])
        payload = jwt.decode(
            token,
            key=key,
            algorithms=["RS256"],
            audience=CLERK_AUDIENCE,
            issuer=CLERK_ISSUER,
        )
        return payload  # Contains user_id, org_id, etc.
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token validation failed: {str(e)}")
