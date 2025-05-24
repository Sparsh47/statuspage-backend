from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from schemas import BaseResponse

ServiceStatus = Literal[
    "operational", "degraded", "partial_outage", "major_outage"
]

class ServiceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    current_status: ServiceStatus = Field(default="operational")

    # Allow ORM attribute retrieval, but for create payload only as user input
    model_config = ConfigDict(from_attributes=True)

class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    slug: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    current_status: Optional[ServiceStatus] = None

    # Removing organization_id from update to prevent FK violations
    model_config = ConfigDict(from_attributes=True)

class ServiceResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    organization_id: Optional[int] = None
    current_status: ServiceStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ServiceStatusUpdateBase(BaseModel):
    service_id: int
    status: ServiceStatus
    message: Optional[str] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ServiceStatusHistoryResponse(BaseResponse):
    service_id: int
    status: ServiceStatus
    message: Optional[str] = None
    created_by: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
