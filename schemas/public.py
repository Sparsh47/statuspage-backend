from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class PublicService(BaseModel):
    id: int
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    organization_id: Optional[int] = None
    current_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PublicIncident(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    type: str
    status: str
    impact: str
    organization_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PublicStatus(BaseModel):
    services: List[PublicService]
    incidents: List[PublicIncident]
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)