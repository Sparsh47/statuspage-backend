from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re
from schemas import BaseResponse


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=50)

    @validator('slug')
    def validate_slug(cls, v):
        if v is not None and not re.match("^[a-z0-9](-?[a-z0-9])*$", v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=50)


class OrganizationResponse(BaseResponse, OrganizationBase):
    is_active: bool


class OrganizationWithDetails(OrganizationResponse):
    services_count: int
    active_incidents_count: int
