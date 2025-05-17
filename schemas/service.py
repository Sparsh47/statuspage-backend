from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from __init import BaseResponse


# Status enum as literals for type checking
ServiceStatus = Literal["Operational", "Degraded Performance", "Partial Outage", "Major Outage"]


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    organization_id: str


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None


class ServiceStatusUpdate(BaseModel):
    status: ServiceStatus


class ServiceResponse(BaseResponse, ServiceBase):
    current_status: ServiceStatus = "Operational"


class ServiceStatusHistoryResponse(BaseResponse):
    service_id: str
    status: ServiceStatus