from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


class ServiceStatus(BaseModel):
    id: str
    name: str
    status: str


class ActiveIncident(BaseModel):
    id: str
    title: str
    status: str
    started_at: datetime
    type: str
    affected_services: List[str]


class RecentIncident(ActiveIncident):
    resolved_at: Optional[datetime] = None


class PublicStatusPage(BaseModel):
    organization: Dict[str, str]
    services: List[ServiceStatus]
    active_incidents: List[ActiveIncident]
    recent_incidents: List[RecentIncident]
    overall_status: str