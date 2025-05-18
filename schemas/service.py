from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from schemas import BaseResponse


# Status enum as literals for type checking
ServiceStatus = Literal["Operational", "Degraded Performance", "Partial Outage", "Major Outage"]


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    current_status: ServiceStatus = "Operational"
    # organization_id: str


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    current_status: Optional[ServiceStatus] = None


class ServiceStatusUpdate(BaseModel):
    status: ServiceStatus


class ServiceResponse(BaseResponse, ServiceBase):
    current_status: ServiceStatus = "Operational"
    model_config = ConfigDict(from_attributes=True)


class ServiceStatusHistoryResponse(BaseResponse):
    service_id: str
    status: ServiceStatus
    updated_at: datetime