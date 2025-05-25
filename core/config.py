# core/config.py

import os
import secrets
from typing import List, Union

from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    ENV: str = os.getenv("ENV", "DEVELOPMENT")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database & cache (read full URLs from env)
    DATABASE_URL: PostgresDsn
    REDIS_URL: RedisDsn

    # CORS origins (comma-separated in env)
    BACKEND_CORS_ORIGINS: List[str] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
            cls, v: Union[str, List[str]]
    ) -> List[str]:
        if isinstance(v, str):
            # split on commas, strip whitespace
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # Clerk (Auth) settings
    CLERK_API_KEY: str
    CLERK_FRONTEND_API: str
    CLERK_JWKS_URL: AnyHttpUrl
    CLERK_ISSUER: AnyHttpUrl
    CLERK_AUDIENCE: str

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
