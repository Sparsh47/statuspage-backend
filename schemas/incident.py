# File: schemas/incident.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime

# Reuse these literals
IncidentType   = Literal["incident", "maintenance"]
IncidentStatus = Literal["investigating", "identified", "monitoring", "resolved"]
IncidentImpact = Literal["minor", "major", "critical"]

class IncidentBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    type: IncidentType   = Field(default="incident")
    status: IncidentStatus = Field(default="investigating")
    impact: IncidentImpact = Field(default="minor")

    # Still optional on create
    organization_id: Optional[int] = None
    created_by:      Optional[int] = None

    scheduled_start: Optional[datetime] = None
    scheduled_end:   Optional[datetime] = None


class IncidentCreate(IncidentBase):
    service_ids: List[int] = []


class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None
    impact: Optional[IncidentImpact] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end:   Optional[datetime] = None


class BaseResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class IncidentResponse(BaseResponse):
    title: str
    description: Optional[str]
    type: IncidentType
    status: IncidentStatus
    impact: IncidentImpact

    # ← Made these optional so returning None passes validation
    organization_id: Optional[int] = None
    created_by:      Optional[int] = None

    resolved_at:      Optional[datetime] = None
    scheduled_start:  Optional[datetime] = None
    scheduled_end:    Optional[datetime] = None
    affected_services: List[int] = []

    model_config = ConfigDict(from_attributes=True)


class IncidentUpdateBase(BaseModel):
    message: str = Field(..., min_length=5)
    status:  IncidentStatus


class IncidentUpdateCreate(IncidentUpdateBase):
    incident_id: int
    created_by:   int


class IncidentUpdateResponse(BaseResponse, IncidentUpdateBase):
    incident_id: int
    created_by:  int

    model_config = ConfigDict(from_attributes=True)


class IncidentWithUpdates(IncidentResponse):
    updates: List[IncidentUpdateResponse] = []
