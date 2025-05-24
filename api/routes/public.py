from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from models.incident import Incident
from models.service import Service
from schemas.public import PublicIncident, PublicService, PublicStatus

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/incidents", response_model=List[PublicIncident])
def list_public_incidents(db: Session = Depends(get_db)):
    incidents = (
        db.query(Incident)
        .order_by(Incident.created_at.desc())
        .limit(10)
        .all()
    )
    return incidents


@router.get("/services", response_model=List[PublicService])
def list_public_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return services


@router.get("/status", response_model=PublicStatus)
def get_public_status(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    incidents = (
        db.query(Incident)
        .filter(Incident.status != "resolved")
        .all()
    )
    return PublicStatus(
        services=services,
        incidents=incidents,
        updated_at=datetime.utcnow(),
    )
