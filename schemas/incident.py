from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime
from schemas import BaseResponse  # adjust import as needed

# --- Enums as Literals ---
IncidentType = Literal["Incident", "Maintenance"]
IncidentStatus = Literal[
    "Investigating",
    "Identified",
    "Monitoring",
    "Resolved",
    "Scheduled",
    "In Progress",
    "Completed",
]

# --- Shared input fields ---
class IncidentBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    incident_type: IncidentType = Field("Incident", alias="type")
    status: IncidentStatus = "Investigating"

    # Coerce from lowercase or mixed-case storage
    @field_validator('incident_type', mode='before')
    @classmethod
    def normalize_type(cls, v):
        if isinstance(v, str):
            return v.capitalize()
        return v

    @field_validator('status', mode='before')
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, str):
            # Title-case each word to match Literal values
            return ' '.join(word.capitalize() for word in v.split())
        return v

# --- Payload for creating a new incident ---
class IncidentCreate(IncidentBase):
    service_ids: List[str] = []

# --- Payload for updating an incident ---
class IncidentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = None
    status: Optional[IncidentStatus] = None

    @field_validator('status', mode='before')
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, str):
            return ' '.join(word.capitalize() for word in v.split())
        return v

# --- Response for an incident ---
class IncidentResponse(BaseResponse):
    id: int
    title: str
    description: Optional[str]
    incident_type: IncidentType = Field(..., alias="type")
    status: IncidentStatus
    organization_id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    affected_services: List[str] = []

    # Validators also apply for response
    @field_validator('incident_type', mode='before')
    @classmethod
    def normalize_type_response(cls, v):
        if isinstance(v, str):
            return v.capitalize()
        return v

    @field_validator('status', mode='before')
    @classmethod
    def normalize_status_response(cls, v):
        if isinstance(v, str):
            return ' '.join(word.capitalize() for word in v.split())
        return v

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

# --- Shared input for incident updates ---
class IncidentUpdateBase(BaseModel):
    message: str = Field(..., min_length=5)
    status: IncidentStatus

    @field_validator('status', mode='before')
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, str):
            return ' '.join(word.capitalize() for word in v.split())
        return v

# --- Payload for creating an incident update ---
class IncidentUpdateCreate(IncidentUpdateBase):
    pass

# --- Response for an incident update ---
class IncidentUpdateResponse(BaseResponse, IncidentUpdateBase):
    incident_id: int
    created_by: int
    updated_at: Optional[datetime] = None  # <- Fix for validation error

# --- Full incident with its updates attached ---
class IncidentWithUpdates(IncidentResponse):
    updates: List[IncidentUpdateResponse] = []