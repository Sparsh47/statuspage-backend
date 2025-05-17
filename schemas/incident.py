from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from __init import BaseResponse


# Enum values as literals for type checking
IncidentType = Literal["Incident", "Maintenance"]
IncidentStatus = Literal["Investigating", "Identified", "Monitoring", "Resolved", "Scheduled", "In Progress", "Completed"]


class IncidentBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    incident_type: IncidentType = "Incident"
    status: IncidentStatus = "Investigating"
    organization_id: str


class IncidentCreate(IncidentBase):
    service_ids: List[str] = []


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None


class IncidentResponse(BaseResponse, IncidentBase):
    created_by: str
    started_at: datetime
    resolved_at: Optional[datetime] = None


class IncidentUpdateBase(BaseModel):
    message: str = Field(..., min_length=5)
    status: IncidentStatus


class IncidentUpdateCreate(IncidentUpdateBase):
    pass


class IncidentUpdateResponse(BaseResponse, IncidentUpdateBase):
    incident_id: str
    created_by: str


class IncidentWithUpdates(IncidentResponse):
    updates: List[IncidentUpdateResponse] = []
    affected_services: List[str] = []