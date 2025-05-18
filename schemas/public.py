# File: schemas/public.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

IncidentStatus = Literal[
    "Investigating",
    "Identified",
    "Monitoring",
    "Resolved",
    "Scheduled",
    "In Progress",
    "Completed",
]

class PublicIncident(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: IncidentStatus
    incident_type: Optional[str] = Field(None, alias="type")
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class PublicService(BaseModel):
    id: int
    name: str
    status: Optional[str] = None  # Allow missing/null status

    model_config = {
        "from_attributes": True
    }

class PublicStatus(BaseModel):
    status: str  # "Operational" or "Degraded"
    affected_services: List[str] = []
    active_incidents: List[PublicIncident] = []
