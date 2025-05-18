# File: api/routes/public.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from models.incident import Incident
from models.service import Service
from schemas.public import PublicIncident, PublicService, PublicStatus

router = APIRouter(prefix="/public", tags=["public"])

@router.get("/incidents", response_model=List[PublicIncident])
def list_public_incidents(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).limit(10).all()
    return incidents


@router.get("/services", response_model=List[PublicService])
def list_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return services


@router.get("/status", response_model=PublicStatus)
def get_public_status(db: Session = Depends(get_db)):
    active_incidents = (
        db.query(Incident)
        .filter(Incident.status.in_(["Investigating", "Identified", "Monitoring"]))
        .order_by(Incident.created_at.desc())
        .all()
    )
    if not active_incidents:
        return PublicStatus(
            status="Operational",
            affected_services=[],
            active_incidents=[]
        )

    # aggregate all affected services
    service_names = set()
    for incident in active_incidents:
        for s in incident.services:
            service_names.add(s.name)

    return PublicStatus(
        status="Degraded",
        affected_services=list(service_names),
        active_incidents=active_incidents
    )
